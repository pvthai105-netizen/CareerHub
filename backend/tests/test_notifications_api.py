from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.routers.notification_router import (
    api_get_notifications,
    api_mark_notification_read,
    api_unread_notification_count,
    router as notification_router,
)
from app.models.job import Job, JobStatus
from app.models.notifications import Notification
from app.models.user import Role, User
from app import deps
from app.services import application_services


@pytest.fixture
def notification_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = db_factory()
    student = User(email="student@example.com", hashed_password="x", role=Role.student)
    employer = User(email="employer@example.com", hashed_password="x", role=Role.employer)
    other = User(email="other@example.com", hashed_password="x", role=Role.student)
    db.add_all([student, employer, other])
    db.commit()
    for user in (student, employer, other):
        db.refresh(user)

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

    yield db, student, employer, other, job
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def add_notification(db, user, title, created_at=None):
    notification = Notification(
        user_id=user.id,
        title=title,
        message=f"Nội dung: {title}",
        created_at=created_at,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def test_notification_routes_require_authenticated_user():
    for route in notification_router.routes:
        assert any(dependency.call is deps.get_current_user for dependency in route.dependant.dependencies)


def test_unread_count_is_scoped_to_user_and_excludes_read(notification_context):
    db, student, employer, _, _ = notification_context
    add_notification(db, student, "Chưa đọc 1")
    add_notification(db, student, "Đã đọc", created_at=None).is_read = True
    add_notification(db, employer, "Của người khác")
    db.commit()

    response = api_unread_notification_count(db, student)

    assert response == {"unread_count": 1}


def test_list_paginates_latest_first_and_only_returns_current_user(notification_context):
    db, student, employer, _, _ = notification_context
    add_notification(db, student, "Mới nhất")
    add_notification(db, student, "Cũ hơn")
    add_notification(db, employer, "Không được lộ")

    response = api_get_notifications(limit=1, offset=1, db=db, current_user=student)

    assert len(response) == 1
    assert response[0].title == "Mới nhất"
    assert all(item.title != "Không được lộ" for item in response)


@pytest.mark.parametrize(("argument", "expected"), [("limit", (1, 100)), ("offset", (0, None))])
def test_list_pagination_query_bounds(argument, expected):
    parameters = {parameter.name: parameter for parameter in notification_router.routes[1].dependant.query_params}
    metadata = parameters[argument].field_info.metadata
    assert any(getattr(bound, "ge", None) == expected[0] for bound in metadata)
    if expected[1] is not None:
        assert any(getattr(bound, "le", None) == expected[1] for bound in metadata)
    else:
        assert not any(hasattr(bound, "le") for bound in metadata)


def test_mark_read_is_idempotent_and_updates_unread_count(notification_context):
    db, student, _, _, _ = notification_context
    notification = add_notification(db, student, "Cập nhật trạng thái")

    first = api_mark_notification_read(notification.id, db, student)
    second = api_mark_notification_read(notification.id, db, student)
    count = api_unread_notification_count(db, student)

    assert first.id == notification.id and first.is_read is True
    assert second.is_read is True
    assert count == {"unread_count": 0}


def test_user_cannot_mark_another_users_notification_read(notification_context):
    db, _, employer, _, _ = notification_context
    notification = add_notification(db, employer, "Riêng tư")

    with pytest.raises(HTTPException) as error:
        api_mark_notification_read(notification.id, db, notification_context[1])
    assert error.value.status_code == 404
    assert db.get(Notification, notification.id).is_read is False


def test_mark_read_returns_404_for_missing_notification(notification_context):
    with pytest.raises(HTTPException) as error:
        api_mark_notification_read(99999, notification_context[0], notification_context[1])
    assert error.value.status_code == 404


def test_new_application_creates_employer_notification(notification_context):
    db, student, employer, _, job = notification_context
    application_services.apply_to_job(
        db,
        student,
        job.job_id,
        "resume.pdf",
        "application/pdf",
        b"%PDF-1.7 test",
        None,
    )

    notification = db.query(Notification).filter_by(user_id=employer.id).one()
    assert notification.title == "Có đơn ứng tuyển mới"
    assert job.title in notification.message
    assert notification.is_read is False


def test_status_change_creates_student_notification(notification_context):
    db, student, employer, _, job = notification_context
    application = application_services.apply_to_job(
        db, student, job.job_id, "resume.pdf", "application/pdf", b"%PDF-1.7 test", None
    )

    application_services.update_application_status(
        db, employer, job.job_id, application.id, application_services.ApplicationStatus.interview
    )

    notification = db.query(Notification).filter_by(user_id=student.id).one()
    assert notification.title == "Trạng thái đơn ứng tuyển đã thay đổi"
    assert "pending sang interview" in notification.message
    assert notification.is_read is False


def test_invalid_status_transition_does_not_create_notification(notification_context):
    db, student, employer, _, job = notification_context
    application = application_services.apply_to_job(
        db, student, job.job_id, "resume.pdf", "application/pdf", b"%PDF-1.7 test", None
    )
    initial_count = db.query(Notification).filter_by(user_id=student.id).count()

    with pytest.raises(HTTPException) as error:
        application_services.update_application_status(
            db,
            employer,
            job.job_id,
            application.id,
            application_services.ApplicationStatus.accepted,
        )

    assert error.value.status_code == 409
    assert db.query(Notification).filter_by(user_id=student.id).count() == initial_count


def test_pagination_boundaries_include_first_and_last_item(notification_context):
    db, student, _, _, _ = notification_context
    add_notification(db, student, "Mục thứ 1")
    add_notification(db, student, "Mục thứ 2")
    add_notification(db, student, "Mục thứ 3")

    first = api_get_notifications(limit=1, offset=0, db=db, current_user=student)
    last = api_get_notifications(limit=1, offset=2, db=db, current_user=student)
    beyond = api_get_notifications(limit=1, offset=3, db=db, current_user=student)

    assert [first[0].title, last[0].title] == ["Mục thứ 3", "Mục thứ 1"]
    assert beyond == []


def test_pagination_is_sorted_newest_first_with_stable_id_tie_break(notification_context):
    db, student, _, _, _ = notification_context
    add_notification(db, student, "Mốc thời gian", created_at=None)
    tied_time = db.query(Notification).filter_by(user_id=student.id).one().created_at
    add_notification(db, student, "ID lớn hơn", created_at=tied_time)

    response = api_get_notifications(limit=2, offset=0, db=db, current_user=student)

    assert [item.title for item in response] == ["ID lớn hơn", "Mốc thời gian"]
