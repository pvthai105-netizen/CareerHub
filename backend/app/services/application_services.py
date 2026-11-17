from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.applications import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import Role, User


MAX_CV_SIZE = 5 * 1024 * 1024
APPLICATION_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "applications"
PDF_MIME_TYPE = "application/pdf"
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def ensure_student(user: User) -> None:
    if user.role != Role.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ sinh viên mới có thể ứng tuyển",
        )


def validate_cv(filename: str | None, content_type: str | None, content: bytes) -> str:
    extension = Path(filename or "").suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="CV phải có định dạng PDF hoặc DOCX")
    if len(content) > MAX_CV_SIZE:
        raise HTTPException(status_code=413, detail="CV không được vượt quá 5 MB")
    if not content:
        raise HTTPException(status_code=400, detail="File CV không được để trống")

    expected_mime = PDF_MIME_TYPE if extension == ".pdf" else DOCX_MIME_TYPE
    if (content_type or "").lower() != expected_mime:
        raise HTTPException(status_code=400, detail="MIME type không khớp với định dạng CV")

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Nội dung file không phải PDF hợp lệ")
    else:
        try:
            with ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())
                valid_docx = "[Content_Types].xml" in names and "word/document.xml" in names
        except BadZipFile:
            valid_docx = False
        if not valid_docx:
            raise HTTPException(status_code=400, detail="Nội dung file không phải DOCX hợp lệ")

    return extension


def apply_to_job(
    db: Session,
    student: User,
    job_id: int,
    filename: str | None,
    content_type: str | None,
    content: bytes,
    cover_letter: str | None,
) -> Application:
    ensure_student(student)
    extension = validate_cv(filename, content_type, content)

    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Tin tuyển dụng không tồn tại")

    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.student_id == student.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bạn đã ứng tuyển tin tuyển dụng này")

    safe_filename = f"{uuid4().hex}{extension}"
    APPLICATION_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    cv_path = APPLICATION_UPLOAD_DIR / safe_filename
    try:
        cv_path.write_bytes(content)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Không thể lưu file CV") from exc

    application = Application(
        job_id=job_id,
        student_id=student.id,
        status=ApplicationStatus.pending,
        cv_file_path=safe_filename,
        cover_letter=cover_letter.strip() if cover_letter and cover_letter.strip() else None,
    )
    try:
        db.add(application)
        db.commit()
        db.refresh(application)
    except IntegrityError as exc:
        db.rollback()
        cv_path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail="Bạn đã ứng tuyển tin tuyển dụng này") from exc
    except Exception:
        db.rollback()
        cv_path.unlink(missing_ok=True)
        raise

    return application
