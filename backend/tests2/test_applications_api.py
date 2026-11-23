from datetime import date
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.applications import Application
from app.models.job import Job, JobStatus
from app.models.user import Role, User
from app.routers.application_router import router
from app.services import application_services


@pytest.fixture
def application_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    employer = User(email="employer@example.com", hashed_password="x", role=Role.employer)
    student = User(email="student@example.com", hashed_password="x", role=Role.student)
    db.add_all([employer, student])
    db.commit()
    db.refresh(student)
    job = Job(
        title="Intern",
        description="Internship",
        industry="Tech",
        location="Hanoi",
        job_type="INTERNSHIP",
        deadline=date.today(),
        status=JobStatus.ACTIVE.value,
        employer_id=employer.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    monkeypatch.setattr(application_services, "APPLICATION_UPLOAD_DIR", tmp_path)

    yield db, student, employer, job, tmp_path

    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def valid_docx_bytes():
    stream = BytesIO()
    with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
    return stream.getvalue()


def test_student_application_route_is_registered():
    routes = {route.path: route.methods for route in router.routes}
    assert "POST" in routes["/api/jobs/{job_id}/applications"]
    assert "GET" in routes["/api/applications/my"]
    assert "POST" in routes["/api/applications/{application_id}/withdraw"]


def test_my_applications_returns_the_students_jobs_and_status(application_context):
    db, student, employer, job, _ = application_context
    submit(db, student, job.job_id, cover_letter="Lời giới thiệu")
    other_student = User(email="other@example.com", hashed_password="x", role=Role.student)
    db.add(other_student)
    db.commit()
    db.refresh(other_student)
    other_job = Job(
        title="Other internship",
        description="Other role",
        industry="Tech",
        location="Hanoi",
        job_type="INTERNSHIP",
        deadline=date.today(),
        status=JobStatus.ACTIVE.value,
        employer_id=employer.id,
    )
    db.add(other_job)
    db.commit()
    db.refresh(other_job)
    submit(db, other_student, other_job.job_id)

    applications = application_services.get_my_applications(db, student)

    assert len(applications) == 1
    assert applications[0]["job_title"] == job.title
    assert applications[0]["status"].value == "pending"
    assert applications[0]["cover_letter"] == "Lời giới thiệu"


def test_student_can_withdraw_pending_application(application_context):
    db, student, _, job, _ = application_context
    application = submit(db, student, job.job_id)

    withdrawn = application_services.withdraw_application(db, student, application.id)

    assert withdrawn.status.value == "withdrawn"
    assert db.query(Application).filter(Application.id == application.id).one()


def test_student_cannot_withdraw_application_after_review(application_context):
    db, student, _, job, _ = application_context
    application = submit(db, student, job.job_id)
    application.status = application_services.ApplicationStatus.reviewed
    db.commit()

    with pytest.raises(HTTPException) as error:
        application_services.withdraw_application(db, student, application.id)

    assert error.value.status_code == 409


def test_student_cannot_view_or_withdraw_another_students_application(application_context):
    db, student, _, job, _ = application_context
    application = submit(db, student, job.job_id)
    other_student = User(email="other@example.com", hashed_password="x", role=Role.student)
    db.add(other_student)
    db.commit()
    db.refresh(other_student)

    with pytest.raises(HTTPException) as error:
        application_services.withdraw_application(db, other_student, application.id)

    assert error.value.status_code == 404


def submit(db, student, job_id, filename="resume.pdf", mime="application/pdf", content=b"%PDF-1.7 test", cover_letter=" Tôi quan tâm "):
    return application_services.apply_to_job(
        db, student, job_id, filename, mime, content, cover_letter
    )


def test_apply_success_saves_safe_filename_and_pending_status(application_context):
    db, student, _, job, upload_dir = application_context
    application = submit(db, student, job.job_id, filename="../../my resume.pdf")

    assert application.status.value == "pending"
    assert application.cover_letter == "Tôi quan tâm"
    assert application.cv_file_path != "../../my resume.pdf"
    assert (upload_dir / application.cv_file_path).is_file()


def test_apply_accepts_valid_docx(application_context):
    db, student, _, job, _ = application_context
    application = submit(
        db,
        student,
        job.job_id,
        filename="resume.docx",
        mime=application_services.DOCX_MIME_TYPE,
        content=valid_docx_bytes(),
    )
    assert application.status.value == "pending"


@pytest.mark.parametrize(
    ("filename", "mime", "content", "expected_status"),
    [
        ("resume.exe", "application/pdf", b"%PDF-1.7", 400),
        ("resume.pdf", "text/plain", b"%PDF-1.7", 400),
        ("resume.pdf", "application/pdf", b"not a pdf", 400),
        ("resume.docx", application_services.DOCX_MIME_TYPE, b"not a zip archive", 400),
        ("resume.pdf", "application/pdf", b"%PDF-1.7" + b"x" * (5 * 1024 * 1024), 413),
    ],
)
def test_apply_rejects_invalid_cv(application_context, filename, mime, content, expected_status):
    db, student, _, job, _ = application_context
    with pytest.raises(HTTPException) as error:
        submit(db, student, job.job_id, filename, mime, content)
    assert error.value.status_code == expected_status


def test_apply_rejects_duplicate_application(application_context):
    db, student, _, job, _ = application_context
    submit(db, student, job.job_id)
    with pytest.raises(HTTPException) as error:
        submit(db, student, job.job_id)
    assert error.value.status_code == 409


def test_apply_rejects_missing_job(application_context):
    db, student, _, _, _ = application_context
    with pytest.raises(HTTPException) as error:
        submit(db, student, 99999)
    assert error.value.status_code == 404


def test_apply_rejects_non_student(application_context):
    db, _, employer, job, _ = application_context
    with pytest.raises(HTTPException) as error:
        submit(db, employer, job.job_id)
    assert error.value.status_code == 403
