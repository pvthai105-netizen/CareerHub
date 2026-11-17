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
)

router = APIRouter(
    prefix="/api/students",
    tags=["students"],
)


# 1. Xem hồ sơ của chính mình
@router.get("/me", response_model=StudentProfileResponse, summary="Xem hồ sơ của mình")
def api_get_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    """Lấy thông tin hồ sơ của chính sinh viên đang đăng nhập."""
    return get_my_student_profile(db, current_user)


# 2. Sửa hồ sơ của chính mình
@router.put("/me", response_model=StudentProfileResponse, summary="Cập nhật hồ sơ của mình")
def api_update_my_profile(
    payload: StudentProfileUpdateSchema,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    """Cập nhật thông tin hồ sơ của chính sinh viên đang đăng nhập."""
    return update_my_student_profile(db, current_user, payload)


# 3. Người khác (nhà tuyển dụng) tìm và xem hồ sơ theo ID
@router.get("/{profile_id}", response_model=StudentProfileResponse, summary="Xem hồ sơ sinh viên theo ID")
def api_get_profile_by_id(
    profile_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Xem thông tin chi tiết hồ sơ sinh viên theo ID (dành cho nhà tuyển dụng/người khác tìm xem)."""
    return get_student_profile_by_id(db, profile_id)