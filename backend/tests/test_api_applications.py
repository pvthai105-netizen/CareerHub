import pytest
from app.models.applications import Application, ApplicationStatus
from app.models.user import Role, User
from app.security import hash_password
from tests.conftest import get_error_message


def test_student_apply_job_success(student_client, active_job, valid_pdf_file):
    """Sinh viên nộp hồ sơ ứng tuyển kèm CV PDF thành công (201 Created)."""
    filename, content, mime = valid_pdf_file
    response = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
        data={"cover_letter": "Em rất mong muốn được ứng tuyển vị trí này."},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["job_id"] == active_job.job_id
    assert data["status"] == "pending"
    assert data["cover_letter"] == "Em rất mong muốn được ứng tuyển vị trí này."
    assert "id" in data


def test_student_cannot_apply_duplicate(student_client, active_job, valid_pdf_file):
    """Sinh viên ứng tuyển 2 lần vào cùng 1 tin bị từ chối (409 Conflict)."""
    filename, content, mime = valid_pdf_file

    # Nộp lần 1 thành công
    res1 = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
    )
    assert res1.status_code == 201

    # Nộp lần 2 trùng lặp -> 409
    res2 = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
    )
    assert res2.status_code == 409
    assert "đã ứng tuyển" in get_error_message(res2)


def test_student_apply_non_existent_job(student_client, valid_pdf_file):
    """Ứng tuyển vào tin không tồn tại trả về 404 Not Found."""
    filename, content, mime = valid_pdf_file
    response = student_client.post(
        "/api/jobs/999999/applications",
        files={"cv": (filename, content, mime)},
    )
    assert response.status_code == 404
    assert "không tồn tại" in get_error_message(response)


def test_student_get_my_applications(student_client, active_job, valid_pdf_file):
    """Sinh viên xem danh sách các đơn đã ứng tuyển của mình (200 OK)."""
    filename, content, mime = valid_pdf_file

    # Nộp 1 đơn ứng tuyển
    student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
        data={"cover_letter": "Lời tự giới thiệu"},
    )

    # Lấy danh sách
    response = student_client.get("/api/applications/my")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["job_title"] == active_job.title
    assert data[0]["status"] == "pending"
    assert data[0]["cover_letter"] == "Lời tự giới thiệu"


def test_student_withdraw_application_success(student_client, active_job, valid_pdf_file):
    """Sinh viên rút đơn ứng tuyển đang ở trạng thái pending (200 OK)."""
    filename, content, mime = valid_pdf_file

    # Nộp đơn
    apply_res = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
    )
    app_id = apply_res.json()["id"]

    # Rút đơn
    withdraw_res = student_client.post(f"/api/applications/{app_id}/withdraw")
    assert withdraw_res.status_code == 200

    data = withdraw_res.json()
    assert data["id"] == app_id
    assert data["status"] == "withdrawn"


def test_student_cannot_withdraw_reviewed_application(student_client, active_job, valid_pdf_file, db_session):
    """Sinh viên không thể rút đơn nếu nhà tuyển dụng đã xét duyệt (409 Conflict)."""
    filename, content, mime = valid_pdf_file

    # Nộp đơn
    apply_res = student_client.post(
        f"/api/jobs/{active_job.job_id}/applications",
        files={"cv": (filename, content, mime)},
    )
    app_id = apply_res.json()["id"]

    # Giả lập nhà tuyển dụng chuyển trạng thái đơn sang reviewed
    app_record = db_session.query(Application).filter(Application.id == app_id).first()
    app_record.status = ApplicationStatus.reviewed
    db_session.commit()

    # Sinh viên cố gắng rút đơn -> 409
    withdraw_res = student_client.post(f"/api/applications/{app_id}/withdraw")
    assert withdraw_res.status_code == 409
    assert "chờ" in get_error_message(withdraw_res).lower()


def test_student_cannot_withdraw_another_students_application(
    student_client, active_job, valid_pdf_file, db_session
):
    """Sinh viên không thể xem hoặc rút đơn của sinh viên khác (404 Not Found)."""
    # Tạo sinh viên thứ hai
    other_student = User(
        email="other_student@test.com",
        hashed_password=hash_password("password123"),
        role=Role.student,
    )
    db_session.add(other_student)
    db_session.commit()
    db_session.refresh(other_student)

    # Đơn của sinh viên khác
    other_app = Application(
        job_id=active_job.job_id,
        student_id=other_student.id,
        status=ApplicationStatus.pending,
        cv_file_path="other_cv.pdf",
    )
    db_session.add(other_app)
    db_session.commit()
    db_session.refresh(other_app)

    # Sinh viên hiện tại cố rút đơn của other_student -> 404
    response = student_client.post(f"/api/applications/{other_app.id}/withdraw")
    assert response.status_code == 404
