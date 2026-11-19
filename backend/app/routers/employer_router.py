from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from datetime import date
from app.models.job import Job, JobStatus

from app import deps
from app.models.user import Role, User
from app.schemas.employer_profile import (
    EmployerProfileResponse,
    EmployerProfileUpdateSchema,
    LogoUploadResponse,
)
from app.services.employer_services import (
    create_or_update_my_employer_profile,
    get_employer_profile_by_id,
    get_my_employer_profile,
    update_employer_profile_by_id,
    upload_company_logo,
)

router = APIRouter(
    prefix="/api/employers",
    tags=["employers"],
)


@router.get("/me", response_model=EmployerProfileResponse, summary="Xem hồ sơ công ty của mình")
@router.get("/profile", response_model=EmployerProfileResponse, include_in_schema=False)
def api_get_my_employer_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.employer)),
):
    """Lấy thông tin hồ sơ công ty của nhà tuyển dụng đang đăng nhập."""
    return get_my_employer_profile(db, current_user)


@router.put("/me", response_model=EmployerProfileResponse, summary="Cập nhật hồ sơ công ty của mình")
@router.put("/profile", response_model=EmployerProfileResponse, include_in_schema=False)
def api_update_my_employer_profile(
    payload: EmployerProfileUpdateSchema,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.employer)),
):
    """Tạo hoặc cập nhật thông tin hồ sơ của chính doanh nghiệp đang đăng nhập."""
    return create_or_update_my_employer_profile(db, current_user, payload)


@router.post("/logo", response_model=LogoUploadResponse, summary="Upload logo công ty")
@router.post("/me/logo", response_model=LogoUploadResponse, include_in_schema=False)
def api_upload_my_logo(
    file: UploadFile = File(..., description="File ảnh logo (.png, .jpg, .jpeg, .webp, tối đa 2MB)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.employer)),
):
    """Upload ảnh đại diện / logo cho công ty của mình (chỉ nhận ảnh, giới hạn 2MB)."""
    return upload_company_logo(db, current_user, file)


@router.get("/{profile_id}", response_model=EmployerProfileResponse, summary="Xem hồ sơ công ty theo ID")
def api_get_employer_profile_by_id(
    profile_id: int,
    db: Session = Depends(deps.get_db),
):
    """Xem thông tin chi tiết hồ sơ công ty theo ID (công khai cho mọi người dùng)."""
    return get_employer_profile_by_id(db, profile_id)

@router.get("/{profile_id}/jobs", summary="Lấy các tin tuyển dụng đang mở của công ty")
def api_get_company_active_jobs(
    profile_id: int,
    db: Session = Depends(deps.get_db),
):
    """Lấy danh sách các tin tuyển dụng ACTIVE chưa hết hạn của công ty."""
    profile = get_employer_profile_by_id(db, profile_id)
    jobs = (
        db.query(Job)
        .filter(
            Job.employer_id == profile.user_id,
            Job.status == JobStatus.ACTIVE.value,
            Job.deadline >= date.today(),
        )
        .all()
    )
    return jobs