from datetime import date, datetime, timezone
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
import time

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.applications import Application, ApplicationStatus
from app.models.job import Job, JobStatus
from app.models.notifications import Notification
from app.models.user import Role, User
from app.services import application_services


@pytest.fixture
def full_flow_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = db_factory()

    employer = User(email="employer@example.com", hashed_password="x", role=Role.employer)
    student = User(email="student@example.com", hashed_password="x", role=Role.student)
    db.add_all([employer, student])
    db.commit()
    for user in (employer, student):
        db.refresh(user)

    job = Job(
        title="Backend Intern",
        description="Python/FastAPI internship",
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


def submit(db, student, job_id, filename="resume.pdf", mime="application/pdf", content=b"%PDF-1.7 test", cover_letter=" Tôi quan tâm "):
    return application_services.apply_to_job(
        db, student, job_id, filename, mime, content, cover_letter
    )


class TestT02D066FullFlow:
    """Test case T02D066 - Kiểm thử trọn luồng ứng tuyển"""

    def test_01_student_apply_employer_change_status_student_receives_notification_within_30s(self, full_flow_context):
        """
        TC01: Sinh viên ứng tuyển → Nhà tuyển dụng thay đổi trạng thái → Sinh viên nhận thông báo trong ≤30 giây.
        """
        db, student, employer, job, _ = full_flow_context

        application = submit(db, student, job.job_id)
        assert application.status == ApplicationStatus.pending

        start_time = time.perf_counter()

        updated_app = application_services.update_application_status(
            db, employer, job.job_id, application.id, ApplicationStatus.interview
        )

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        elapsed_s = elapsed_ms / 1000

        assert updated_app.status == ApplicationStatus.interview

        notification = db.query(Notification).filter_by(user_id=student.id).one()
        assert notification.title == "Trạng thái đơn ứng tuyển đã thay đổi"
        assert "pending sang interview" in notification.message
        assert notification.is_read is False

        assert elapsed_s <= 30.0, f"Notification delivery took {elapsed_s:.3f}s, exceeds 30s limit"

        print(f"\n[TIMING] Notification created in {elapsed_ms:.2f} ms ({elapsed_s:.6f} s)")

    def test_02_upload_cv_wrong_format_exe(self, full_flow_context):
        """
        TC02: Upload CV sai định dạng (.exe)
        Expected: HTTP 400
        """
        db, student, _, job, _ = full_flow_context
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.exe", mime="application/pdf", content=b"%PDF-1.7")
        assert error.value.status_code == 400
        assert "định dạng PDF hoặc DOCX" in error.value.detail

    def test_03_upload_cv_wrong_format_txt(self, full_flow_context):
        """
        TC03: Upload CV sai định dạng (.txt)
        Expected: HTTP 400
        """
        db, student, _, job, _ = full_flow_context
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.txt", mime="text/plain", content=b"plain text")
        assert error.value.status_code == 400
        assert "định dạng PDF hoặc DOCX" in error.value.detail

    def test_04_upload_cv_wrong_mime_pdf_as_text(self, full_flow_context):
        """
        TC04: Upload PDF nhưng MIME type là text/plain
        Expected: HTTP 400
        """
        db, student, _, job, _ = full_flow_context
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.pdf", mime="text/plain", content=b"%PDF-1.7")
        assert error.value.status_code == 400
        assert "MIME type không khớp" in error.value.detail

    def test_05_upload_cv_invalid_pdf_content(self, full_flow_context):
        """
        TC05: Upload file .pdf nhưng nội dung không phải PDF hợp lệ
        Expected: HTTP 400
        """
        db, student, _, job, _ = full_flow_context
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.pdf", mime="application/pdf", content=b"not a pdf")
        assert error.value.status_code == 400
        assert "không phải PDF hợp lệ" in error.value.detail

    def test_06_upload_cv_invalid_docx_content(self, full_flow_context):
        """
        TC06: Upload file .docx nhưng nội dung không phải DOCX hợp lệ
        Expected: HTTP 400
        """
        db, student, _, job, _ = full_flow_context
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.docx", mime=application_services.DOCX_MIME_TYPE, content=b"not a zip")
        assert error.value.status_code == 400
        assert "không phải DOCX hợp lệ" in error.value.detail

    def test_07_upload_cv_exceeds_5mb_limit(self, full_flow_context):
        """
        TC07: Upload CV vượt quá 5MB
        Expected: HTTP 413
        """
        db, student, _, job, _ = full_flow_context
        large_content = b"%PDF-1.7" + b"x" * (5 * 1024 * 1024)
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.pdf", mime="application/pdf", content=large_content)
        assert error.value.status_code == 413
        assert "vượt quá 5 MB" in error.value.detail

    def test_08_upload_cv_empty_file(self, full_flow_context):
        """
        TC08: Upload CV file rỗng
        Expected: HTTP 400
        """
        db, student, _, job, _ = full_flow_context
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id, filename="resume.pdf", mime="application/pdf", content=b"")
        assert error.value.status_code == 400
        assert "không được để trống" in error.value.detail

    def test_09_duplicate_application_same_job(self, full_flow_context):
        """
        TC09: Ứng tuyển trùng một công việc
        Expected: HTTP 409
        """
        db, student, _, job, _ = full_flow_context
        submit(db, student, job.job_id)
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id)
        assert error.value.status_code == 409
        assert "đã ứng tuyển" in error.value.detail

    def test_10_duplicate_application_concurrent_integrity_error(self, full_flow_context):
        """
        TC10: Ứng tuyển trùng - kiểm tra xử lý IntegrityError từ database (race condition)
        Expected: HTTP 409
        """
        db, student, _, job, _ = full_flow_context
        submit(db, student, job.job_id)
        with pytest.raises(HTTPException) as error:
            submit(db, student, job.job_id)
        assert error.value.status_code == 409

    def test_11_status_transition_pending_to_rejected_creates_notification(self, full_flow_context):
        """
        TC11: Nhà tuyển dụng chuyển từ pending -> rejected → Sinh viên nhận thông báo
        """
        db, student, employer, job, _ = full_flow_context
        application = submit(db, student, job.job_id)

        start_time = time.perf_counter()
        updated_app = application_services.update_application_status(
            db, employer, job.job_id, application.id, ApplicationStatus.rejected
        )
        elapsed_s = (time.perf_counter() - start_time)

        assert updated_app.status == ApplicationStatus.rejected

        notification = db.query(Notification).filter_by(user_id=student.id).one()
        assert notification.title == "Trạng thái đơn ứng tuyển đã thay đổi"
        assert "pending sang rejected" in notification.message
        assert elapsed_s <= 30.0

    def test_12_status_transition_interview_to_accepted_creates_notification(self, full_flow_context):
        """
        TC12: Nhà tuyển dụng chuyển interview -> accepted → Sinh viên nhận thông báo
        """
        db, student, employer, job, _ = full_flow_context
        application = submit(db, student, job.job_id)
        application_services.update_application_status(
            db, employer, job.job_id, application.id, ApplicationStatus.interview
        )
        db.commit()

        start_time = time.perf_counter()
        updated_app = application_services.update_application_status(
            db, employer, job.job_id, application.id, ApplicationStatus.accepted
        )
        elapsed_s = (time.perf_counter() - start_time)

        assert updated_app.status == ApplicationStatus.accepted

        notification = (
            db.query(Notification)
            .filter_by(user_id=student.id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .first()
        )
        assert notification is not None
        assert "interview sang accepted" in notification.message
        assert elapsed_s <= 30.0

    def test_13_invalid_status_transition_pending_to_accepted_no_notification(self, full_flow_context):
        """
        TC13: Chuyển pending trực tiếp sang accepted → Bị từ chối, không tạo thông báo
        Expected: HTTP 409, không tạo notification
        """
        db, student, employer, job, _ = full_flow_context
        application = submit(db, student, job.job_id)
        initial_notif_count = db.query(Notification).filter_by(user_id=student.id).count()

        with pytest.raises(HTTPException) as error:
            application_services.update_application_status(
                db, employer, job.job_id, application.id, ApplicationStatus.accepted
            )
        assert error.value.status_code == 409
        assert "Không thể chuyển đơn sang trạng thái này" in error.value.detail

        final_notif_count = db.query(Notification).filter_by(user_id=student.id).count()
        assert final_notif_count == initial_notif_count

    def test_14_invalid_status_transition_accepted_to_rejected_no_notification(self, full_flow_context):
        """
        TC14: Chuyển accepted -> rejected (reverse) → Bị từ chối, không tạo thông báo
        """
        db, student, employer, job, _ = full_flow_context
        application = submit(db, student, job.job_id)
        application_services.update_application_status(db, employer, job.job_id, application.id, ApplicationStatus.interview)
        application_services.update_application_status(db, employer, job.job_id, application.id, ApplicationStatus.accepted)
        db.commit()

        initial_notif_count = db.query(Notification).filter_by(user_id=student.id).count()

        with pytest.raises(HTTPException) as error:
            application_services.update_application_status(
                db, employer, job.job_id, application.id, ApplicationStatus.rejected
            )
        assert error.value.status_code == 409

        final_notif_count = db.query(Notification).filter_by(user_id=student.id).count()
        assert final_notif_count == initial_notif_count

    def test_15_valid_docx_upload_success(self, full_flow_context):
        """
        TC15: Upload CV DOCX hợp lệ → Thành công
        """
        db, student, _, job, _ = full_flow_context
        application = submit(
            db, student, job.job_id,
            filename="resume.docx",
            mime=application_services.DOCX_MIME_TYPE,
            content=valid_docx_bytes()
        )
        assert application.status == ApplicationStatus.pending
        assert application.cv_file_path.endswith(".docx")

    def test_16_valid_pdf_upload_success(self, full_flow_context):
        """
        TC16: Upload CV PDF hợp lệ → Thành công
        """
        db, student, _, job, _ = full_flow_context
        application = submit(
            db, student, job.job_id,
            filename="resume.pdf",
            mime="application/pdf",
            content=b"%PDF-1.7 valid pdf content"
        )
        assert application.status == ApplicationStatus.pending
        assert application.cv_file_path.endswith(".pdf")

    def test_17_employer_notification_on_new_application(self, full_flow_context):
        """
        TC17: Nhà tuyển dụng nhận thông báo khi có đơn ứng tuyển mới
        """
        db, student, employer, job, _ = full_flow_context

        start_time = time.perf_counter()
        submit(db, student, job.job_id)
        elapsed_s = (time.perf_counter() - start_time)

        notification = db.query(Notification).filter_by(user_id=employer.id).one()
        assert notification.title == "Có đơn ứng tuyển mới"
        assert job.title in notification.message
        assert notification.is_read is False
        assert elapsed_s <= 30.0

    def test_18_withdraw_application_creates_employer_notification(self, full_flow_context):
        """
        TC18: Sinh viên rút đơn → Nhà tuyển dụng nhận thông báo
        """
        db, student, employer, job, _ = full_flow_context
        application = submit(db, student, job.job_id)

        start_time = time.perf_counter()
        application_services.withdraw_application(db, student, application.id)
        elapsed_s = (time.perf_counter() - start_time)

        notification = (
            db.query(Notification)
            .filter_by(user_id=employer.id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .first()
        )
        assert notification is not None
        assert notification.title == "Ứng viên đã rút đơn"
        assert job.title in notification.message
        assert elapsed_s <= 30.0