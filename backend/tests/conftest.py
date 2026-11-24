import sys
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

# Đảm bảo thư mục backend luôn nằm trong sys.path dù chạy pytest ở thư mục nào
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.employee_profiles import EmployerProfile
from app.models.job import Job, JobStatus, JobType
from app.models.user import Role, User
from app.security import create_access_token, hash_password
from app.services import application_services


def get_error_message(response) -> str:
    """Trích xuất thông báo lỗi từ response (hỗ trợ cả message của BaseResponse và detail của HTTPException)."""
    try:
        data = response.json()
        if isinstance(data, dict):
            return str(data.get("message") or data.get("detail") or "")
        return str(data)
    except Exception:
        return response.text


@pytest.fixture
def db_session():
    """Tạo database SQLite in-memory độc lập cho mỗi test case."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    """TestClient không có Authorization header."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def student_user(db_session):
    """Tài khoản sinh viên hợp lệ."""
    user = User(
        email="student@test.com",
        hashed_password=hash_password("password123"),
        role=Role.student,
        is_locked=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def locked_student_user(db_session):
    """Tài khoản sinh viên bị khóa."""
    user = User(
        email="locked_student@test.com",
        hashed_password=hash_password("password123"),
        role=Role.student,
        is_locked=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def employer_user(db_session):
    """Tài khoản nhà tuyển dụng hợp lệ kèm profile công ty."""
    user = User(
        email="employer@test.com",
        hashed_password=hash_password("password123"),
        role=Role.employer,
        is_locked=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = EmployerProfile(
        user_id=user.id,
        company_name="TechCorp Solutions",
        is_verified=True,
    )
    db_session.add(profile)
    db_session.commit()
    return user


@pytest.fixture
def other_employer_user(db_session):
    """Nhà tuyển dụng thứ hai (dùng để kiểm thử không được sửa tin của nhau)."""
    user = User(
        email="other_employer@test.com",
        hashed_password=hash_password("password123"),
        role=Role.employer,
        is_locked=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = EmployerProfile(
        user_id=user.id,
        company_name="OtherCorp",
        is_verified=True,
    )
    db_session.add(profile)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Tài khoản quản trị viên (Admin)."""
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        role=Role.admin,
        is_locked=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_client(db_session, student_user):
    """Client đã đăng nhập với vai trò Sinh viên."""
    token = create_access_token(student_user.id, student_user.role)
    with TestClient(app) as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c


@pytest.fixture
def employer_client(db_session, employer_user):
    """Client đã đăng nhập với vai trò Nhà tuyển dụng."""
    token = create_access_token(employer_user.id, employer_user.role)
    with TestClient(app) as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c


@pytest.fixture
def other_employer_client(db_session, other_employer_user):
    """Client đã đăng nhập với vai trò Nhà tuyển dụng 2."""
    token = create_access_token(other_employer_user.id, other_employer_user.role)
    with TestClient(app) as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c


@pytest.fixture
def admin_client(db_session, admin_user):
    """Client đã đăng nhập với vai trò Admin."""
    token = create_access_token(admin_user.id, admin_user.role)
    with TestClient(app) as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c


@pytest.fixture
def active_job(db_session, employer_user):
    """Tin tuyển dụng mẫu đang ở trạng thái ACTIVE."""
    job = Job(
        title="Python Backend Developer",
        description="Phát triển API và xử lý dữ liệu với FastAPI",
        industry="Công nghệ thông tin",
        location="Hà Nội",
        salary_min=15000000,
        salary_max=25000000,
        job_type=JobType.FULL_TIME.value,
        deadline=date.today() + timedelta(days=30),
        status=JobStatus.ACTIVE.value,
        employer_id=employer_user.id,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def valid_pdf_file():
    """Tạo file PDF mẫu hợp lệ dưới dạng tuple (filename, bytes, mime)."""
    content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    return ("cv_test.pdf", content, "application/pdf")


@pytest.fixture
def valid_docx_file():
    """Tạo file DOCX mẫu hợp lệ với cấu trúc ZIP XML."""
    stream = BytesIO()
    with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
    return (
        "cv_test.docx",
        stream.getvalue(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@pytest.fixture(autouse=True)
def mock_cv_upload_dir(tmp_path, monkeypatch):
    """Tự động hướng thư mục upload CV sang thư mục tạm tmp_path của pytest."""
    monkeypatch.setattr(application_services, "APPLICATION_UPLOAD_DIR", tmp_path / "applications")
