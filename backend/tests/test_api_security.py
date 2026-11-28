import io
from pathlib import Path
from fastapi import HTTPException
from app.models.employee_profiles import EmployerProfile
from app.models.user import Role, User
from app.services.employer_services import upload_company_logo
from tests.conftest import get_error_message


def test_student_cannot_create_job_rbac_check(student_client):
    """Sinh viên gửi yêu cầu tạo tin tuyển dụng bị chặn ngay từ Router (403 Forbidden)."""
    payload = {
        "title": "Intern Python",
        "description": "Chi tiết công việc",
        "industry": "IT",
        "location": "Hà Nội",
        "job_type": "INTERNSHIP",
    }
    response = student_client.post("/jobs", json=payload)
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_student_cannot_access_my_jobs_list(student_client):
    """Sinh viên truy cập danh sách tin của nhà tuyển dụng bị chặn 403."""
    response = student_client.get("/jobs/my-jobs")
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_student_cannot_update_job(student_client):
    """Sinh viên gửi yêu cầu cập nhật tin bị chặn 403."""
    response = student_client.put("/jobs/my-jobs/1", json={"title": "Updated Title"})
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_student_cannot_delete_job(student_client):
    """Sinh viên gửi yêu cầu xóa tin bị chặn 403."""
    response = student_client.delete("/jobs/my-jobs/1")
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_student_cannot_change_job_status(student_client):
    """Sinh viên đổi trạng thái tin bị chặn 403."""
    response = student_client.patch("/jobs/1/status", json={"status": "ACTIVE"})
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_upload_logo_fake_png_magic_bytes_rejected(employer_client):
    """Upload file đuôi .png nhưng nội dung là text thường bị từ chối 400 do sai chữ ký số (Magic Bytes)."""
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("fake_image.png", b"echo 'hacked'", "image/png")},
    )
    assert response.status_code == 400
    assert "chỉ chấp nhận định dạng ảnh" in get_error_message(response)


def test_upload_logo_extension_and_content_type_mismatch_rejected(employer_client):
    """Upload file mã độc đuôi .php kèm Content-Type giả mạo image/png bị từ chối 400."""
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("webshell.php", b"<?php phpinfo(); ?>", "image/png")},
    )
    assert response.status_code == 400
    assert "chỉ chấp nhận định dạng ảnh" in get_error_message(response)


def test_upload_logo_valid_png_accepted(employer_client):
    """Upload file PNG có Magic Bytes hợp lệ thành công 200."""
    valid_png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (b"\x00" * 32)
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("logo.png", valid_png_content, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "logo_url" in data
    assert data["logo_url"].startswith("/uploads/logos/logo_")

    # Dọn dẹp file test
    relative_path = data["logo_url"].lstrip("/")
    created_file = Path(__file__).resolve().parents[2] / "frontend" / relative_path
    if created_file.exists():
        created_file.unlink()


def test_upload_logo_valid_jpeg_accepted(employer_client):
    """Upload file JPG có Magic Bytes hợp lệ thành công 200."""
    valid_jpg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF" + (b"\x00" * 32)
    response = employer_client.post(
        "/api/employers/logo",
        files={"file": ("logo.jpg", valid_jpg_content, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "logo_url" in data
    assert data["logo_url"].startswith("/uploads/logos/logo_")

    # Dọn dẹp file test
    relative_path = data["logo_url"].lstrip("/")
    created_file = Path(__file__).resolve().parents[2] / "frontend" / relative_path
    if created_file.exists():
        created_file.unlink()


def test_gitignore_contains_security_exclusions():
    """Kiểm tra file .gitignore có đầy đủ cấu hình chặn .env và secrets."""
    gitignore_path = Path(__file__).resolve().parents[2] / ".gitignore"
    assert gitignore_path.exists()
    content = gitignore_path.read_text(encoding="utf-8")
    assert ".env*" in content
    assert "!.env.example" in content
    assert "*.pem" in content
    assert "*.key" in content
