from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import deps
from app.models.user import Role, User
from app.schemas.student_profile import (
    StudentProfileResponse,
    StudentProfileUpdateSchema,
)
from app.services.student_services import (
    get_my_student_profile,
    update_my_student_profile,
    get_student_profile_by_id,
    update_student_profile_by_id,
)

router = APIRouter(
    prefix="/api/students",
    tags=["students"],
)


@router.get("/me", response_model=StudentProfileResponse, summary="Xem hồ sơ của mình")
@router.get("/profile", response_model=StudentProfileResponse, include_in_schema=False)
def api_get_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    """Lấy thông tin hồ sơ của sinh viên đang đăng nhập."""
    return get_my_student_profile(db, current_user)


@router.put("/me", response_model=StudentProfileResponse, summary="Cập nhật hồ sơ của mình")
@router.put("/profile", response_model=StudentProfileResponse, include_in_schema=False)
def api_update_my_profile(
    payload: StudentProfileUpdateSchema,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    """Cập nhật thông tin hồ sơ của chính sinh viên đang đăng nhập."""
    return update_my_student_profile(db, current_user, payload)


@router.get("/{profile_id}", response_model=StudentProfileResponse, summary="Xem hồ sơ theo ID")
def api_get_profile_by_id(
    profile_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Xem thông tin chi tiết hồ sơ sinh viên theo ID."""
    return get_student_profile_by_id(db, profile_id)


@router.put("/{profile_id}", response_model=StudentProfileResponse, summary="Cập nhật hồ sơ theo ID (chỉ chủ hồ sơ)")
def api_update_profile_by_id(
    profile_id: int,
    payload: StudentProfileUpdateSchema,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Cập nhật hồ sơ theo ID (chặn nếu không phải chủ hồ sơ)."""
    return update_student_profile_by_id(db, current_user, profile_id, payload)