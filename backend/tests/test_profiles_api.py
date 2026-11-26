import shutil
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models.employee_profiles import EmployerProfile
from app.models.job import Job, JobStatus, JobType
from app.models.user import Role, User
from app.routers import employer_router, student_router
from app.security import create_access_token, hash_password
from utils.exceptions import exception_handlers


def _get_error_message(response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            return str(data.get("message") or data.get("detail") or "")
        return str(data)
    except Exception:
        return response.text


def _cleanup_uploaded_logo(logo_url: str, uploads_existed: bool) -> None:
    if not logo_url:
        return
    frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
    created_file = frontend_dir / logo_url.lstrip("/")
    if created_file.exists():
        created_file.unlink()
    uploads_dir = frontend_dir / "uploads"
    if not uploads_existed and uploads_dir.exists():
        shutil.rmtree(uploads_dir, ignore_errors=True)


@pytest.fixture
def profile_context():
    """Tạo FastAPI app cô lập (không import app.main) và SQLite in-memory."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = db_factory()

    test_app = FastAPI(title="Profile Test App")
    exception_handlers(test_app)
    test_app.include_router(student_router.router)
    test_app.include_router(employer_router.router)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    test_app.dependency_overrides[get_db] = override_get_db

    student = User(email="student@test.com", hashed_password=hash_password("password123"), role=Role.student)
    other_student = User(email="other_student@test.com", hashed_password=hash_password("password123"), role=Role.student)
    employer = User(email="employer@test.com", hashed_password=hash_password("password123"), role=Role.employer)
    admin = User(email="admin@test.com", hashed_password=hash_password("password123"), role=Role.admin)
    db.add_all([student, other_student, employer, admin])
    db.commit()
    for u in (student, other_student, employer, admin):
        db.refresh(u)

    emp_profile = EmployerProfile(user_id=employer.id, company_name="TechCorp Solutions", is_verified=True)
    db.add(emp_profile)
    db.commit()
    db.refresh(emp_profile)

    anon_client = TestClient(test_app)
    student_client = TestClient(test_app)
    student_client.headers["Authorization"] = f"Bearer {create_access_token(student.id, student.role)}"
    other_student_client = TestClient(test_app)
    other_student_client.headers["Authorization"] = f"Bearer {create_access_token(other_student.id, other_student.role)}"
    employer_client = TestClient(test_app)
    employer_client.headers["Authorization"] = f"Bearer {create_access_token(employer.id, employer.role)}"
    admin_client = TestClient(test_app)
    admin_client.headers["Authorization"] = f"Bearer {create_access_token(admin.id, admin.role)}"

    uploads_existed = (Path(__file__).resolve().parents[2] / "frontend" / "uploads").exists()

    yield {
        "app": test_app,
        "db": db,
        "student": student,
        "other_student": other_student,
        "employer": employer,
        "admin": admin,
        "emp_profile": emp_profile,
        "anon_client": anon_client,
        "student_client": student_client,
        "other_student_client": other_student_client,
        "employer_client": employer_client,
        "admin_client": admin_client,
        "uploads_existed": uploads_existed,
    }

    for c in (anon_client, student_client, other_student_client, employer_client, admin_client):
        c.close()
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# ==============================================================================
# MODULE 1: HỒ SƠ SINH VIÊN (/api/students/*)
# ==============================================================================


def test_stu_01_get_my_profile_auto_create(profile_context):
    """[Đúng] GET /api/students/me lần đầu tự khởi tạo hồ sơ mặc định."""
    res = profile_context["student_client"].get("/api/students/me")
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == profile_context["student"].id
    assert data["email"] == profile_context["student"].email
    assert data["full_name"] == "student"
    assert data["desired_job_type"] == "BOTH"


def test_stu_02_get_profile_alias_endpoint(profile_context):
    """[Đúng] GET /api/students/profile (alias) hoạt động giống /me."""
    res = profile_context["student_client"].get("/api/students/profile")
    assert res.status_code == 200
    assert res.json()["user_id"] == profile_context["student"].id


def test_stu_03_update_my_profile_valid(profile_context):
    """[Đúng] PUT /api/students/me cập nhật đầy đủ thông tin hợp lệ."""
    payload = {
        "full_name": "Vũ Nhất Thống",
        "phone": "0901234567",
        "university": "Học viện Công nghệ Bưu chính Viễn thông",
        "major": "Công nghệ thông tin",
        "bio": "Sinh viên năm 3 chuyên ngành CNTT.",
        "skills": "Python, FastAPI, SQL",
        "desired_job_type": "INTERNSHIP",
        "avatar_url": "https://example.com/avatar.png",
    }
    res = profile_context["student_client"].put("/api/students/me", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Vũ Nhất Thống"
    assert data["phone"] == "0901234567"
    assert data["desired_job_type"] == "INTERNSHIP"


def test_stu_04_update_phone_plus84_and_strip(profile_context):
    """[Đúng] Chấp nhận SĐT đầu +84 và tự động strip khoảng trắng."""
    res = profile_context["student_client"].put(
        "/api/students/me",
        json={
            "full_name": "  Nguyễn Văn A  ",
            "phone": " +84912345678 ",
            "university": "  PTIT  ",
            "major": "  Kỹ thuật phần mềm  ",
            "desired_job_type": "PART_TIME",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Nguyễn Văn A"
    assert data["phone"] == "+84912345678"
    assert data["university"] == "PTIT"


def test_stu_05_get_and_update_by_id_owner_success(profile_context):
    """[Đúng] Xem theo ID và chính chủ sửa qua PUT /api/students/{id}."""
    created = profile_context["student_client"].get("/api/students/me").json()
    profile_id = created["id"]

    res_get = profile_context["employer_client"].get(f"/api/students/{profile_id}")
    assert res_get.status_code == 200

    res_put = profile_context["student_client"].put(
        f"/api/students/{profile_id}",
        json={"full_name": "Tên Đã Cập Nhật", "skills": "Python, Docker"},
    )
    assert res_put.status_code == 200
    assert res_put.json()["full_name"] == "Tên Đã Cập Nhật"


def test_stu_06_unauthenticated_and_wrong_role_rejected(profile_context):
    """[Sai] Chưa đăng nhập (401) hoặc sai vai trò (403) bị chặn."""
    anon = profile_context["anon_client"]
    assert anon.get("/api/students/me").status_code == 401
    assert anon.put("/api/students/me", json={"full_name": "Test"}).status_code == 401
    assert anon.get("/api/students/1").status_code == 401

    assert profile_context["employer_client"].get("/api/students/me").status_code == 403
    assert profile_context["admin_client"].get("/api/students/me").status_code == 403


def test_stu_07_other_user_cannot_update_profile_by_id(profile_context):
    """[Sai] Sinh viên khác hoặc Employer không được sửa hồ sơ của người khác (403)."""
    profile_id = profile_context["student_client"].get("/api/students/me").json()["id"]
    assert profile_context["other_student_client"].put(
        f"/api/students/{profile_id}", json={"full_name": "Hack"}
    ).status_code == 403
    assert profile_context["employer_client"].put(
        f"/api/students/{profile_id}", json={"full_name": "Hack"}
    ).status_code == 403


def test_stu_08_not_found_profile_404(profile_context):
    """[Sai] profile_id không tồn tại trả về 404."""
    sc = profile_context["student_client"]
    assert sc.get("/api/students/999999").status_code == 404
    assert sc.put("/api/students/999999", json={"full_name": "Test"}).status_code == 404


def test_stu_09_invalid_name_phone_and_enum_rejected(profile_context):
    """[Sai] full_name rỗng/khoảng trắng, SĐT sai định dạng, enum sai bị từ chối (422)."""
    sc = profile_context["student_client"]
    assert sc.put("/api/students/me", json={"full_name": ""}).status_code == 422
    assert sc.put("/api/students/me", json={"full_name": "   "}).status_code == 422
    for bad_phone in ("090123456", "09012345678", "1901234567", "+8490123456", "09012abc67"):
        assert sc.put("/api/students/me", json={"phone": bad_phone}).status_code == 422
    assert sc.put("/api/students/me", json={"desired_job_type": "FULL_TIME"}).status_code == 422


def test_stu_10_boundary_field_lengths(profile_context):
    """[Biên] Đúng max_length (100/150/255) hợp lệ (200); vượt +1 bị từ chối (422)."""
    sc = profile_context["student_client"]
    res_ok = sc.put(
        "/api/students/me",
        json={
            "full_name": "A" * 100,
            "university": "U" * 150,
            "major": "M" * 100,
            "avatar_url": "https://a.vn/" + ("x" * (255 - 13)),
        },
    )
    assert res_ok.status_code == 200

    assert sc.put("/api/students/me", json={"full_name": "A" * 101}).status_code == 422
    assert sc.put("/api/students/me", json={"university": "U" * 151}).status_code == 422
    assert sc.put("/api/students/me", json={"major": "M" * 101}).status_code == 422
    assert sc.put("/api/students/me", json={"avatar_url": "x" * 256}).status_code == 422


def test_stu_11_boundary_clear_optional_field_with_empty_string(profile_context):
    """[Biên - Bug Check] Gửi '' để xóa trường tùy chọn đã lưu (phone/bio) phải về null."""
    sc = profile_context["student_client"]
    assert sc.put("/api/students/me", json={"phone": "0901234567", "bio": "Bio cũ"}).status_code == 200
    res = sc.put("/api/students/me", json={"phone": "", "bio": ""})
    assert res.status_code == 200
    assert res.json()["phone"] is None, f"phone cũ không bị xóa khi gửi '', vẫn là {res.json()['phone']!r}"
    assert res.json()["bio"] is None, f"bio cũ không bị xóa khi gửi '', vẫn là {res.json()['bio']!r}"


# ==============================================================================
# MODULE 2: HỒ SƠ CÔNG TY, UPLOAD LOGO & CÔNG KHAI (/api/employers/*)
# ==============================================================================


def test_emp_01_get_my_profile_auto_create(profile_context):
    """[Đúng] GET /api/employers/me lần đầu với employer mới tự tạo hồ sơ mặc định."""
    db = profile_context["db"]
    fresh = User(email="fresh_hr@company.vn", hashed_password=hash_password("password123"), role=Role.employer)
    db.add(fresh)
    db.commit()
    db.refresh(fresh)

    with TestClient(profile_context["app"]) as c:
        c.headers["Authorization"] = f"Bearer {create_access_token(fresh.id, fresh.role)}"
        res = c.get("/api/employers/me")
        assert res.status_code == 200
        assert res.json()["company_name"] == "Công ty của fresh_hr"
        assert res.json()["is_verified"] is False


def test_emp_02_update_employer_profile_and_alias(profile_context):
    """[Đúng] PUT /api/employers/me và GET /api/employers/profile cập nhật thành công."""
    ec = profile_context["employer_client"]
    res = ec.put(
        "/api/employers/me",
        json={
            "company_name": "CareerHub Tech JSC",
            "contact_name": "Trần Minh Anh",
            "phone": "+84987654321",
            "company_website": "https://careerhub.vn",
            "address": "123 Nguyễn Trãi, Hà Nội",
            "tax_code": "0109998887",
        },
    )
    assert res.status_code == 200
    assert res.json()["company_name"] == "CareerHub Tech JSC"
    assert ec.get("/api/employers/profile").json()["tax_code"] == "0109998887"


def test_emp_03_public_company_detail_and_active_jobs(profile_context):
    """[Đúng / Biên] Công khai xem công ty và lọc đúng tin ACTIVE chưa hết hạn (kể cả deadline == today)."""
    db = profile_context["db"]
    employer = profile_context["employer"]
    profile_id = profile_context["emp_profile"].id
    anon = profile_context["anon_client"]

    db.add_all(
        [
            Job(
                title="Active Future",
                description="D",
                industry="IT",
                location="HN",
                job_type=JobType.FULL_TIME.value,
                deadline=date.today() + timedelta(days=3),
                status=JobStatus.ACTIVE.value,
                employer_id=employer.id,
            ),
            Job(
                title="Active Today",
                description="D",
                industry="IT",
                location="HN",
                job_type=JobType.INTERNSHIP.value,
                deadline=date.today(),
                status=JobStatus.ACTIVE.value,
                employer_id=employer.id,
            ),
            Job(
                title="Draft Hidden",
                description="D",
                industry="IT",
                location="HN",
                job_type=JobType.FULL_TIME.value,
                deadline=date.today() + timedelta(days=3),
                status=JobStatus.DRAFT.value,
                employer_id=employer.id,
            ),
            Job(
                title="Expired Hidden",
                description="D",
                industry="IT",
                location="HN",
                job_type=JobType.FULL_TIME.value,
                deadline=date.today() - timedelta(days=1),
                status=JobStatus.ACTIVE.value,
                employer_id=employer.id,
            ),
        ]
    )
    db.commit()

    assert anon.get(f"/api/employers/{profile_id}").status_code == 200
    res_jobs = anon.get(f"/api/employers/{profile_id}/jobs")
    assert res_jobs.status_code == 200
    titles = [j["title"] for j in res_jobs.json()]
    assert "Active Future" in titles
    assert "Active Today" in titles
    assert "Draft Hidden" not in titles
    assert "Expired Hidden" not in titles


def test_emp_04_upload_logo_valid_formats_and_alias(profile_context):
    """[Đúng] Upload logo hợp lệ (.png, .jpg, .webp) và alias /me/logo."""
    ec = profile_context["employer_client"]
    uploads_existed = profile_context["uploads_existed"]
    samples = [
        ("logo.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 32, "image/png", "/api/employers/logo"),
        ("logo.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 32, "image/jpeg", "/api/employers/logo"),
        ("logo.webp", b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 32, "image/webp", "/api/employers/me/logo"),
    ]
    for fname, content, mime, endpoint in samples:
        res = ec.post(endpoint, files={"file": (fname, content, mime)})
        assert res.status_code == 200
        try:
            assert res.json()["logo_url"].startswith("/uploads/logos/logo_")
        finally:
            _cleanup_uploaded_logo(res.json().get("logo_url", ""), uploads_existed)


def test_emp_05_auth_rbac_and_not_found(profile_context):
    """[Sai] Chưa đăng nhập (401), sai vai trò (403) và ID không tồn tại (404)."""
    anon = profile_context["anon_client"]
    assert anon.get("/api/employers/me").status_code == 401
    assert anon.put("/api/employers/me", json={"company_name": "X"}).status_code == 401
    assert anon.post("/api/employers/logo", files={"file": ("a.png", b"\x89PNG", "image/png")}).status_code == 401

    assert profile_context["student_client"].get("/api/employers/me").status_code == 403
    assert profile_context["admin_client"].get("/api/employers/me").status_code == 403
    assert anon.get("/api/employers/999999").status_code == 404
    assert anon.get("/api/employers/999999/jobs").status_code == 404


def test_emp_06_invalid_company_name_phone_and_logo(profile_context):
    """[Sai] company_name rỗng, SĐT sai, logo sai định dạng (.txt) hoặc rỗng (0 bytes)."""
    ec = profile_context["employer_client"]
    assert ec.put("/api/employers/me", json={"company_name": ""}).status_code == 422
    assert ec.put("/api/employers/me", json={"company_name": "   "}).status_code == 422
    for bad_phone in ("01234", "+8412345", "090123456a"):
        assert ec.put("/api/employers/me", json={"phone": bad_phone}).status_code == 422

    r_txt = ec.post("/api/employers/logo", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert r_txt.status_code == 400
    assert "chỉ chấp nhận định dạng ảnh" in _get_error_message(r_txt)

    r_empty = ec.post("/api/employers/logo", files={"file": ("empty.png", b"", "image/png")})
    assert r_empty.status_code == 400


def test_emp_07_boundary_lengths_and_logo_2mb_limit(profile_context):
    """[Biên] Độ dài trường tối đa và giới hạn dung lượng logo đúng 2MB vs 2MB + 1 byte."""
    ec = profile_context["employer_client"]
    uploads_existed = profile_context["uploads_existed"]

    assert ec.put(
        "/api/employers/me",
        json={"company_name": "C" * 200, "contact_name": "N" * 100, "tax_code": "1" * 50, "address": "A" * 255},
    ).status_code == 200
    assert ec.put("/api/employers/me", json={"company_name": "C" * 201}).status_code == 422
    assert ec.put("/api/employers/me", json={"tax_code": "1" * 51}).status_code == 422

    header = b"\x89PNG\r\n\x1a\n"
    exact_2mb = header + (b"\x00" * (2 * 1024 * 1024 - len(header)))
    r_ok = ec.post("/api/employers/logo", files={"file": ("exact.png", exact_2mb, "image/png")})
    try:
        assert r_ok.status_code == 200
    finally:
        if r_ok.status_code == 200:
            _cleanup_uploaded_logo(r_ok.json().get("logo_url", ""), uploads_existed)

    r_fail = ec.post("/api/employers/logo", files={"file": ("over.png", exact_2mb + b"\x00", "image/png")})
    assert r_fail.status_code == 400
    assert "2.0MB" in _get_error_message(r_fail)


def test_emp_08_bug_check_spoofed_exe_logo_rejected(profile_context):
    """[Sai/Biên - Bug Check] File .exe giả mạo MIME image/png phải bị từ chối (400)."""
    ec = profile_context["employer_client"]
    res = ec.post("/api/employers/logo", files={"file": ("malware.exe", b"MZ\x90\x00fake", "image/png")})
    if res.status_code == 200:
        _cleanup_uploaded_logo(res.json().get("logo_url", ""), profile_context["uploads_existed"])
    assert res.status_code == 400, f"Chấp nhận file .exe giả MIME image/png ({res.status_code})"


def test_emp_09_bug_check_clear_optional_field_with_empty_string(profile_context):
    """[Biên - Bug Check] Gửi address='' hoặc phone='' để xóa trắng trường đã lưu phải trả về null."""
    ec = profile_context["employer_client"]
    assert ec.put("/api/employers/me", json={"address": "Hà Nội", "phone": "0901234567"}).status_code == 200
    res = ec.put("/api/employers/me", json={"address": "", "phone": ""})
    assert res.status_code == 200
    assert res.json()["address"] is None, f"address cũ không bị xóa khi gửi '', vẫn là {res.json()['address']!r}"
    assert res.json()["phone"] is None, f"phone cũ không bị xóa khi gửi '', vẫn là {res.json()['phone']!r}"
