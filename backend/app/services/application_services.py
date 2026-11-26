from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.applications import Application, ApplicationStatus
from app.models.job import Job
from app.models.notifications import Notification
from app.models.user import Role, User
from app.models.student_profiles import StudentProfile


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
        db.add(Notification(
            user_id=job.employer_id,
            title="Có đơn ứng tuyển mới",
            message=f"Bạn vừa nhận được đơn ứng tuyển cho vị trí {job.title}.",
        ))
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


def get_my_applications(db: Session, student: User) -> list[dict]:
    ensure_student(student)
    rows = (
        db.query(Application, Job.title)
        .join(Job, Application.job_id == Job.job_id)
        .filter(Application.student_id == student.id)
        .order_by(Application.applied_at.desc(), Application.id.desc())
        .all()
    )
    return [
        {
            "id": application.id,
            "job_id": application.job_id,
            "job_title": title,
            "status": application.status,
            "applied_at": application.applied_at,
            "cover_letter": application.cover_letter,
        }
        for application, title in rows
    ]


def withdraw_application(db: Session, student: User, application_id: int) -> Application:
    ensure_student(student)
    existing = (
        db.query(Application)
        .filter(Application.id == application_id, Application.student_id == student.id)
        .first()
    )
    if existing is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn ứng tuyển")
    if existing.status != ApplicationStatus.pending:
        raise HTTPException(status_code=409, detail="Chỉ có thể rút đơn đang ở trạng thái Chờ")

    result = db.execute(
        update(Application)
        .where(
            Application.id == application_id,
            Application.student_id == student.id,
            Application.status == ApplicationStatus.pending,
        )
        .values(status=ApplicationStatus.withdrawn)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Trạng thái đơn đã thay đổi, không thể rút")

    db.add(Notification(
        user_id=existing.job.employer_id,
        title="Ứng viên đã rút đơn",
        message=f"Ứng viên đã rút đơn ứng tuyển vị trí {existing.job.title}.",
    ))
    db.commit()
    db.expire_all()
    return db.query(Application).filter(Application.id == application_id).one()


def _get_employer_job(db: Session, employer: User, job_id: int) -> Job:
    if employer.role != Role.employer:
        raise HTTPException(status_code=403, detail="Chỉ nhà tuyển dụng mới được thực hiện thao tác này")
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Tin tuyển dụng không tồn tại")
    if job.employer_id != employer.id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập tin tuyển dụng này")
    return job


def get_job_applications(
    db: Session,
    employer: User,
    job_id: int,
    application_status: ApplicationStatus | None = None,
) -> list[dict]:
    _get_employer_job(db, employer, job_id)
    query = (
        db.query(Application, User.email, StudentProfile.full_name, StudentProfile.phone)
        .join(User, Application.student_id == User.id)
        .outerjoin(StudentProfile, StudentProfile.user_id == User.id)
        .filter(Application.job_id == job_id)
    )
    if application_status is not None:
        query = query.filter(Application.status == application_status)

    return [
        {
            "id": application.id,
            "job_id": application.job_id,
            "student_id": application.student_id,
            "student_name": full_name or email,
            "student_email": email,
            "student_phone": phone,
            "status": application.status,
            "applied_at": application.applied_at,
            "cover_letter": application.cover_letter,
            "has_cv": bool(application.cv_file_path),
        }
        for application, email, full_name, phone in query.order_by(
            Application.applied_at.desc(), Application.id.desc()
        ).all()
    ]


def update_application_status(
    db: Session,
    employer: User,
    job_id: int,
    application_id: int,
    new_status: ApplicationStatus,
) -> Application:
    _get_employer_job(db, employer, job_id)
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.job_id == job_id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn ứng tuyển")

    allowed_transitions = {
        ApplicationStatus.pending: {ApplicationStatus.interview, ApplicationStatus.rejected},
        ApplicationStatus.interview: {ApplicationStatus.accepted, ApplicationStatus.rejected},
    }
    if new_status not in allowed_transitions.get(application.status, set()):
        raise HTTPException(status_code=409, detail="Không thể chuyển đơn sang trạng thái này")

    previous_status = application.status
    application.status = new_status
    db.add(Notification(
        user_id=application.student_id,
        title="Trạng thái đơn ứng tuyển đã thay đổi",
        message=f"Đơn ứng tuyển vị trí {application.job.title} chuyển từ {previous_status.value} sang {new_status.value}.",
    ))
    db.commit()
    db.refresh(application)
    return application


def get_application_cv_path(
    db: Session, employer: User, job_id: int, application_id: int
) -> tuple[Path, str]:
    _get_employer_job(db, employer, job_id)
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.job_id == job_id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn ứng tuyển")
    if not application.cv_file_path:
        raise HTTPException(status_code=404, detail="Ứng viên chưa có CV")

    upload_dir = APPLICATION_UPLOAD_DIR.resolve()
    cv_path = (upload_dir / application.cv_file_path).resolve()
    if cv_path.parent != upload_dir or not cv_path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy file CV")
    if cv_path.suffix.lower() not in {".pdf", ".docx"}:
        raise HTTPException(status_code=404, detail="Định dạng CV không hợp lệ")
    media_type = PDF_MIME_TYPE if cv_path.suffix.lower() == ".pdf" else DOCX_MIME_TYPE
    return cv_path, media_type
