import pytest
from app.models.user import User
from tests.conftest import get_error_message


def test_register_student_success(client):
    """Đăng ký tài khoản Sinh viên thành công (201 Created)."""
    payload = {
        "email": "new_student@example.com",
        "password": "Password123@",
        "role": "student",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "new_student@example.com"
    assert data["role"] == "student"
    assert data["is_locked"] is False
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_employer_success(client):
    """Đăng ký tài khoản Nhà tuyển dụng thành công (201 Created)."""
    payload = {
        "email": "new_employer@example.com",
        "password": "Password123@",
        "role": "employer",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "new_employer@example.com"
    assert data["role"] == "employer"
    assert data["is_locked"] is False
    assert "id" in data


def test_register_duplicate_email(client, student_user):
    """Đăng ký với email đã tồn tại bị từ chối (409 Conflict)."""
    payload = {
        "email": student_user.email,
        "password": "AnotherPassword123@",
        "role": "student",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "đã được sử dụng" in get_error_message(response)


def test_register_invalid_email_format(client):
    """Đăng ký với định dạng email sai bị từ chối (422 Unprocessable Entity)."""
    payload = {
        "email": "not-an-email",
        "password": "Password123@",
        "role": "student",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client, student_user):
    """Đăng nhập với email và mật khẩu đúng (200 OK, trả JWT access token)."""
    payload = {
        "email": student_user.email,
        "password": "password123",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"
    assert len(data["access_token"]) > 20


def test_login_wrong_password(client, student_user):
    """Đăng nhập sai mật khẩu bị từ chối (401 Unauthorized)."""
    payload = {
        "email": student_user.email,
        "password": "WrongPassword999",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Email hoặc mật khẩu không đúng" in get_error_message(response)


def test_login_non_existent_email(client):
    """Đăng nhập với email chưa từng đăng ký (401 Unauthorized)."""
    payload = {
        "email": "nonexistent_account@example.com",
        "password": "password123",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Email hoặc mật khẩu không đúng" in get_error_message(response)


def test_login_locked_account(client, locked_student_user):
    """Đăng nhập tài khoản đã bị khóa (403 Forbidden)."""
    payload = {
        "email": locked_student_user.email,
        "password": "password123",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 403
    assert "Tài khoản đã bị khoá" in get_error_message(response)


def test_get_me_success(student_client, student_user):
    """Lấy thông tin tài khoản hiện tại qua token Bearer (200 OK)."""
    response = student_client.get("/api/auth/me")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == student_user.id
    assert data["email"] == student_user.email
    assert data["role"] == "student"
    assert data["is_locked"] is False


def test_get_me_unauthorized(client):
    """Gọi endpoint /api/auth/me khi chưa đăng nhập (401 Unauthorized)."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
