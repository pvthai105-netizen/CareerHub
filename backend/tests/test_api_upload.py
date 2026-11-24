from pathlib import Path
from app.models.applications import Application
from tests.conftest import get_error_message


def test_upload_cv_valid_pdf_success(student_client, active_job, valid_pdf_file, db_session):
    """Upload CV định dạng PDF hợp lệ thành công (201 Created)."""
    filename, content, mime = valid_pdf_file
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "pending"
    assert "id" in data

    # Kiểm tra file đã được lưu an toàn trong database
    app_record = db_session.query(Application).filter(Application.id == data["id"]).first()
    assert app_record is not None
    assert app_record.cv_file_path.endswith(".pdf")


def test_upload_cv_valid_docx_success(student_client, active_job, valid_docx_file, db_session):
    """Upload CV định dạng DOCX hợp lệ thành công (201 Created)."""
    filename, content, mime = valid_docx_file
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "pending"
    assert "id" in data

    # Kiểm tra file đã được lưu an toàn trong database
    app_record = db_session.query(Application).filter(Application.id == data["id"]).first()
    assert app_record is not None
    assert app_record.cv_file_path.endswith(".docx")


def test_upload_cv_invalid_extension_rejected(student_client, active_job):
    """Upload CV định dạng file không được phép (.exe, .txt) bị từ chối (400 Bad Request)."""
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": ("malicious.exe", b"executable file content", "application/pdf")},
    )
    assert response.status_code == 400
    assert "CV phải có định dạng PDF hoặc DOCX" in get_error_message(response)


def test_upload_cv_corrupted_pdf_rejected(student_client, active_job):
    """Upload file đuôi .pdf nhưng nội dung giả mạo (không bắt đầu bằng %PDF-) bị từ chối (400 Bad Request)."""
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": ("fake.pdf", b"This is fake text content, not a PDF", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Nội dung file không phải PDF hợp lệ" in get_error_message(response)


def test_upload_cv_corrupted_docx_rejected(student_client, active_job):
    """Upload file đuôi .docx nhưng nội dung không phải ZIP hợp lệ bị từ chối (400 Bad Request)."""
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": ("fake.docx", b"Plain text not a zip", mime)},
    )
    assert response.status_code == 400
    assert "Nội dung file không phải DOCX hợp lệ" in get_error_message(response)


def test_upload_cv_exceeds_max_size_rejected(student_client, active_job):
    """Upload CV vượt quá dung lượng tối đa 5 MB bị từ chối (413 Payload Too Large)."""
    # 5MB + 128 bytes
    oversized_content = b"%PDF-1.4 " + (b"0" * (5 * 1024 * 1024 + 128))
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": ("oversized.pdf", oversized_content, "application/pdf")},
    )
    assert response.status_code == 413
    assert "vượt quá 5 MB" in get_error_message(response)


def test_upload_company_logo_success(employer_client):
    """Nhà tuyển dụng upload logo công ty định dạng PNG hợp lệ thành công (200 OK)."""
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("company_logo.png", png_bytes, "image/png")},
    )
    assert response.status_code == 200

    data = response.json()
    assert "logo_url" in data
    assert data["logo_url"].startswith("/uploads/logos/logo_")
    assert "thành công" in data["message"].lower()

    # Dọn dẹp file logo test vừa tạo sau test
    relative_path = data["logo_url"].lstrip("/")
    created_file = Path(__file__).resolve().parents[2] / "frontend" / relative_path
    if created_file.exists():
        created_file.unlink()


def test_upload_company_logo_invalid_type_rejected(employer_client):
    """Upload logo công ty bằng định dạng không phải ảnh bị từ chối (400 Bad Request)."""
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("document.txt", b"plain text content", "text/plain")},
    )
    assert response.status_code == 400
    assert "chỉ chấp nhận định dạng ảnh" in get_error_message(response)


def test_upload_company_logo_empty_file_rejected(employer_client):
    """Upload logo có dung lượng 0 byte bị từ chối (400 Bad Request)."""
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400
    assert "Tệp tải lên rỗng" in get_error_message(response)


def test_upload_company_logo_exceeds_limit_rejected(employer_client):
    """Upload logo vượt quá dung lượng tối đa 2 MB bị từ chối (400 Bad Request)."""
    oversized_image = b"\x89PNG\r\n\x1a\n" + (b"0" * (2 * 1024 * 1024 + 1024))
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("large_logo.png", oversized_image, "image/png")},
    )
    assert response.status_code == 400
    assert "vượt quá giới hạn tối đa 2.0MB" in get_error_message(response)
