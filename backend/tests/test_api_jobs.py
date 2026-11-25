from datetime import date, timedelta
from app.models.job import Job, JobStatus
from tests.conftest import get_error_message


def test_employer_create_job_success(employer_client):
    """Nhà tuyển dụng tạo tin tuyển dụng thành công (201 Created)."""
    payload = {
        "title": "React Frontend Engineer",
        "description": "Lập trình giao diện người dùng với ReactJS và Tailwind",
        "industry": "Công nghệ thông tin",
        "location": "Đà Nẵng",
        "salary_min": 12000000,
        "salary_max": 20000000,
        "job_type": "FULL_TIME",
        "deadline": (date.today() + timedelta(days=20)).isoformat(),
    }
    response = employer_client.post("/jobs", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "React Frontend Engineer"
    assert data["status"] == "DRAFT"
    assert data["location"] == "Đà Nẵng"
    assert "job_id" in data


def test_create_job_with_invalid_salary_range(employer_client):
    """Tạo tin tuyển dụng với mức lương min > max bị từ chối (422 Unprocessable Content)."""
    payload = {
        "title": "Invalid Salary Role",
        "description": "Mô tả công việc",
        "industry": "IT",
        "location": "Hà Nội",
        "salary_min": 30000000,
        "salary_max": 10000000,  # min > max
        "job_type": "FULL_TIME",
        "deadline": (date.today() + timedelta(days=20)).isoformat(),
    }
    response = employer_client.post("/jobs", json=payload)
    assert response.status_code == 422
    assert "tối thiểu không được lớn hơn" in get_error_message(response)


def test_create_job_with_past_deadline(employer_client):
    """Tạo tin tuyển dụng với deadline trong quá khứ bị từ chối (422 Unprocessable Entity)."""
    payload = {
        "title": "Past Deadline Job",
        "description": "Mô tả công việc",
        "industry": "IT",
        "location": "Hà Nội",
        "salary_min": 10000000,
        "salary_max": 20000000,
        "job_type": "FULL_TIME",
        "deadline": (date.today() - timedelta(days=5)).isoformat(),  # Quá khứ
    }
    response = employer_client.post("/jobs", json=payload)
    assert response.status_code == 422
    assert "không được là quá khứ" in get_error_message(response)


def test_get_public_jobs_list(client, active_job):
    """Người dùng công khai xem danh sách tin tuyển dụng (200 OK)."""
    response = client.get("/jobs/")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    job_ids = [item["job_id"] for item in data["items"]]
    assert active_job.job_id in job_ids


def test_employer_get_my_jobs(employer_client, active_job):
    """Nhà tuyển dụng xem danh sách tin do chính mình đăng (200 OK)."""
    response = employer_client.get("/jobs/my-jobs")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["items"][0]["job_id"] == active_job.job_id
    assert data["items"][0]["title"] == active_job.title


def test_employer_get_my_job_detail(employer_client, active_job):
    """Nhà tuyển dụng xem chi tiết một tin của mình (200 OK)."""
    response = employer_client.get(f"/jobs/my-jobs/{active_job.job_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["job_id"] == active_job.job_id
    assert data["title"] == active_job.title


def test_employer_update_own_job(employer_client, active_job):
    """Nhà tuyển dụng cập nhật thông tin tin tuyển dụng của mình (200 OK)."""
    payload = {
        "title": "Senior Python Backend Developer",
        "description": "Nâng cấp và bảo trì hệ thống backend với hiệu năng cao",
        "industry": "Công nghệ thông tin",
        "location": "Hà Nội",
        "salary_min": 25000000,
        "salary_max": 40000000,
        "job_type": "FULL_TIME",
        "deadline": (date.today() + timedelta(days=45)).isoformat(),
    }
    response = employer_client.put(f"/jobs/my-jobs/{active_job.job_id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Senior Python Backend Developer"
    assert data["salary_min"] == 25000000
    assert data["salary_max"] == 40000000


def test_employer_cannot_modify_other_employer_job(other_employer_client, active_job):
    """Nhà tuyển dụng không thể sửa tin của nhà tuyển dụng khác (403 Forbidden)."""
    payload = {
        "title": "Hacked Title",
        "description": "Cố tình sửa tin của người khác",
        "industry": "IT",
        "location": "HCM",
        "salary_min": 10000000,
        "salary_max": 15000000,
        "job_type": "FULL_TIME",
        "deadline": (date.today() + timedelta(days=10)).isoformat(),
    }
    response = other_employer_client.put(f"/jobs/my-jobs/{active_job.job_id}", json=payload)
    assert response.status_code == 403
    assert "Không có quyền truy cập" in get_error_message(response)


def test_employer_cannot_delete_other_employer_job(other_employer_client, active_job):
    """Nhà tuyển dụng không thể xóa tin của nhà tuyển dụng khác (403 Forbidden)."""
    response = other_employer_client.delete(f"/jobs/my-jobs/{active_job.job_id}")
    assert response.status_code == 403
    assert "Không có quyền truy cập" in get_error_message(response)


def test_employer_change_job_status(employer_client, active_job):
    """Nhà tuyển dụng thay đổi trạng thái tin tuyển dụng (200 OK)."""
    payload = {"status": "PAUSED"}
    response = employer_client.patch(f"/jobs/{active_job.job_id}/status", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "PAUSED"


def test_employer_delete_job_success(employer_client, active_job, db_session):
    """Nhà tuyển dụng xóa tin của chính mình (204 No Content)."""
    response = employer_client.delete(f"/jobs/my-jobs/{active_job.job_id}")
    assert response.status_code == 204

    # Kiểm tra tin đã thực sự bị xóa khỏi database
    deleted = db_session.query(Job).filter(Job.job_id == active_job.job_id).first()
    assert deleted is None


def test_get_non_existent_job_returns_404(employer_client):
    """Xem chi tiết tin không tồn tại trả về 404 Not Found."""
    response = employer_client.get("/jobs/my-jobs/999999")
    assert response.status_code == 404
    assert "Tin không tồn tại" in get_error_message(response)
