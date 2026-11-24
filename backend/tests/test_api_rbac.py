from datetime import date, timedelta
from tests.conftest import get_error_message


def test_unauthenticated_request_rejected(client, active_job):
    """Yêu cầu không kèm token xác thực bị từ chối với mã 401 Unauthorized."""
    # 1. Xem thông tin cá nhân
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 401

    # 2. Tạo tin tuyển dụng
    res_post_job = client.post(
        "/jobs",
        json={
            "title": "Backend Dev",
            "description": "Mô tả",
            "industry": "IT",
            "location": "Hà Nội",
            "job_type": "FULL_TIME",
            "deadline": (date.today() + timedelta(days=10)).isoformat(),
        },
    )
    assert res_post_job.status_code == 401

    # 3. Xem đơn ứng tuyển của tôi
    res_my_apps = client.get("/api/applications/my")
    assert res_my_apps.status_code == 401

    # 4. Xem danh sách người dùng quyền Admin
    res_admin = client.get("/api/admin/users")
    assert res_admin.status_code == 401


def test_student_cannot_create_job(student_client):
    """Sinh viên không được phép tạo tin tuyển dụng (403 Forbidden)."""
    payload = {
        "title": "Fresher Python",
        "description": "Chi tiết công việc",
        "industry": "Công nghệ thông tin",
        "location": "Hà Nội",
        "salary_min": 8000000,
        "salary_max": 12000000,
        "job_type": "FULL_TIME",
        "deadline": (date.today() + timedelta(days=15)).isoformat(),
    }
    response = student_client.post("/jobs", json=payload)
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_student_cannot_access_employer_my_jobs(student_client):
    """Sinh viên không thể xem danh sách tin quản lý của nhà tuyển dụng (403 Forbidden)."""
    response = student_client.get("/jobs/my-jobs")
    assert response.status_code == 403
    assert "Chỉ nhà tuyển dụng" in get_error_message(response)


def test_student_cannot_upload_company_logo(student_client):
    """Sinh viên không thể upload logo công ty (403 Forbidden)."""
    response = student_client.post(
        "/api/employers/logo",
        files={"file": ("logo.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )
    assert response.status_code == 403
    msg = get_error_message(response).lower()
    assert "không có quyền" in msg or "nhà tuyển dụng" in msg


def test_employer_cannot_apply_to_job(employer_client, active_job, valid_pdf_file):
    """Nhà tuyển dụng không thể nộp đơn ứng tuyển công việc (403 Forbidden)."""
    filename, content, mime = valid_pdf_file
    response = employer_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
        data={"cover_letter": "Tôi muốn ứng tuyển"},
    )
    assert response.status_code == 403
    msg = get_error_message(response).lower()
    assert "không có quyền" in msg or "sinh viên" in msg


def test_employer_cannot_access_student_my_applications(employer_client):
    """Nhà tuyển dụng không thể xem danh sách đơn ứng tuyển cá nhân (403 Forbidden)."""
    response = employer_client.get("/api/applications/my")
    assert response.status_code == 403
    assert "không có quyền" in get_error_message(response).lower()


def test_student_cannot_access_admin_users(student_client):
    """Sinh viên bị chặn truy cập API quản trị viên (403 Forbidden)."""
    response = student_client.get("/api/admin/users")
    assert response.status_code == 403
    assert "không có quyền truy cập" in get_error_message(response).lower()


def test_employer_cannot_access_admin_users(employer_client):
    """Nhà tuyển dụng bị chặn truy cập API quản trị viên (403 Forbidden)."""
    response = employer_client.get("/api/admin/users")
    assert response.status_code == 403
    assert "không có quyền truy cập" in get_error_message(response).lower()


def test_admin_can_access_admin_users(admin_client):
    """Tài khoản Admin truy cập API quản trị viên thành công (200 OK)."""
    response = admin_client.get("/api/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_admin_only_probe_endpoint(student_client, employer_client, admin_client):
    """Kiểm tra endpoint thử quyền /api/auth/admin-only với cả 3 vai trò."""
    # Sinh viên -> 403
    res_student = student_client.get("/api/auth/admin-only")
    assert res_student.status_code == 403

    # Nhà tuyển dụng -> 403
    res_employer = employer_client.get("/api/auth/admin-only")
    assert res_employer.status_code == 403

    # Admin -> 200
    res_admin = admin_client.get("/api/auth/admin-only")
    assert res_admin.status_code == 200
    assert "Xin chào admin" in res_admin.json()["message"]
