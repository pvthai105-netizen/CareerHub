import json
from io import BytesIO
from types import SimpleNamespace

import pytest
from docx import Document
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.cv_analyses import CvAnalysis
from app.models.user import Role, User
from app.routers.cv_analysis_router import router
from app.services import cv_analysis_services
from app.services.application_services import DOCX_MIME_TYPE, PDF_MIME_TYPE


@pytest.fixture
def cv_analysis_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    student = User(email="student@example.com", hashed_password="x", role=Role.student)
    db.add(student)
    db.commit()
    db.refresh(student)
    monkeypatch.setattr(cv_analysis_services, "CV_ANALYSIS_UPLOAD_DIR", tmp_path)

    yield db, student, tmp_path

    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_docx(text: str = "", table_text: str = "") -> bytes:
    document = Document()
    if text:
        document.add_paragraph(text)
    if table_text:
        table = document.add_table(rows=1, cols=1)
        table.cell(0, 0).text = table_text
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


def create_text_pdf(text: str) -> bytes:
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
        + content
        + b"\nendstream",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for object_id, pdf_object in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{object_id} 0 obj\n".encode("ascii") + pdf_object + b"\nendobj\n"

    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii")
    pdf += b"".join(
        f"{offset:010d} 00000 n \n".encode("ascii")
        for offset in offsets[1:]
    )
    pdf += (
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode("ascii")
    return pdf


def fake_gemini(monkeypatch, response_text: str):
    class FakeModels:
        contents = None

        def generate_content(self, **kwargs):
            self.contents = kwargs["contents"]
            return SimpleNamespace(text=response_text)

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    client = FakeClient()
    monkeypatch.setattr(cv_analysis_services, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(cv_analysis_services.genai, "Client", lambda **_kwargs: client)
    return client


def analysis_json() -> str:
    return json.dumps(
        {
            "summary": "Sinh viên CNTT có kinh nghiệm dự án Python.",
            "strengths": ["Có dự án Python thực tế."],
            "weaknesses": ["Chưa nêu kết quả định lượng."],
            "missing_skills": ["Kiểm thử tự động"],
            "score": 82,
            "improvement_suggestions": ["Bổ sung số liệu cho từng dự án."],
        },
        ensure_ascii=False,
    )


def test_cv_analysis_route_is_registered():
    routes = {route.path: route.methods for route in router.routes}
    assert "POST" in routes["/api/students/me/cv-analyses"]


def test_docx_extraction_includes_paragraphs_and_tables():
    text, extension = cv_analysis_services.extract_cv_text(
        "resume.docx",
        DOCX_MIME_TYPE,
        create_docx("Kỹ sư phần mềm, sử dụng Python.", "Dự án: xây dựng REST API"),
    )

    assert extension == ".docx"
    assert "Kỹ sư phần mềm" in text
    assert "Dự án: xây dựng REST API" in text


def test_pdf_extraction_reads_selectable_text():
    text, extension = cv_analysis_services.extract_cv_text(
        "resume.pdf",
        PDF_MIME_TYPE,
        create_text_pdf("Candidate Python Developer"),
    )

    assert extension == ".pdf"
    assert "Candidate Python Developer" in text


def test_empty_docx_is_rejected_before_llm_call():
    with pytest.raises(HTTPException) as error:
        cv_analysis_services.extract_cv_text(
            "empty.docx",
            DOCX_MIME_TYPE,
            create_docx(),
        )

    assert error.value.status_code == 422
    assert "PDF scan" in error.value.detail


def test_scanned_pdf_is_rejected_when_no_text_can_be_extracted(monkeypatch):
    class FakePDF:
        pages = [SimpleNamespace(extract_text=lambda: None)]

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(cv_analysis_services.pdfplumber, "open", lambda _content: FakePDF())

    with pytest.raises(HTTPException) as error:
        cv_analysis_services.extract_cv_text(
            "scan.pdf",
            PDF_MIME_TYPE,
            b"%PDF-1.7 placeholder",
        )

    assert error.value.status_code == 422
    assert "PDF scan" in error.value.detail


def test_analysis_saves_score_feedback_and_private_file(
    cv_analysis_context,
    monkeypatch,
):
    db, student, upload_dir = cv_analysis_context
    client = fake_gemini(monkeypatch, analysis_json())

    result = cv_analysis_services.analyze_cv(
        db,
        student,
        "resume.docx",
        DOCX_MIME_TYPE,
        create_docx("Sinh viên CNTT, dự án Python"),
    )

    record = db.query(CvAnalysis).one()
    stored_feedback = json.loads(record.feedback)
    assert result.id == record.id
    assert result.filename == "resume.docx"
    assert result.score == 82
    assert record.score == 82
    assert stored_feedback["missing_skills"] == ["Kiểm thử tự động"]
    assert (upload_dir / record.cv_file_url).is_file()
    assert "Sinh viên CNTT, dự án Python" in client.models.contents


def test_analysis_rejects_invalid_llm_json_without_saving_file(
    cv_analysis_context,
    monkeypatch,
):
    db, student, upload_dir = cv_analysis_context
    fake_gemini(monkeypatch, '{"summary":"bad","score":120}')

    with pytest.raises(HTTPException) as error:
        cv_analysis_services.analyze_cv(
            db,
            student,
            "resume.docx",
            DOCX_MIME_TYPE,
            create_docx("Sinh viên CNTT"),
        )

    assert error.value.status_code == 502
    assert db.query(CvAnalysis).count() == 0
    assert list(upload_dir.iterdir()) == []


def test_analysis_requires_gemini_configuration(cv_analysis_context, monkeypatch):
    db, student, upload_dir = cv_analysis_context
    monkeypatch.setattr(cv_analysis_services, "GEMINI_API_KEY", "")

    with pytest.raises(HTTPException) as error:
        cv_analysis_services.analyze_cv(
            db,
            student,
            "resume.docx",
            DOCX_MIME_TYPE,
            create_docx("Sinh viên CNTT"),
        )

    assert error.value.status_code == 503
    assert db.query(CvAnalysis).count() == 0
    assert list(upload_dir.iterdir()) == []


def test_analysis_rejects_non_student(cv_analysis_context):
    db, _, _ = cv_analysis_context
    employer = User(email="employer@example.com", hashed_password="x", role=Role.employer)

    with pytest.raises(HTTPException) as error:
        cv_analysis_services.analyze_cv(
            db,
            employer,
            "resume.docx",
            DOCX_MIME_TYPE,
            create_docx("Sinh viên CNTT"),
        )

    assert error.value.status_code == 403
