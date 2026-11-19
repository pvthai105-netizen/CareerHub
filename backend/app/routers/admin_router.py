from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import deps
from app.models.user import Role, User
from app.schemas.admin import (
    UserDetailResponse,
    UserListResponse,
    UserStatusUpdateSchema,
)
from app.services.admin_services import (
    get_user_detail,
    get_users_list,
    update_user_lock_status,
)

router = APIRouter(
    prefix="/api/admin/users",
    tags=["admin-users"],
    # Yêu cầu bắt buộc quyền ADMIN cho toàn bộ endpoints trong router này
    dependencies=[Depends(deps.require_roles(Role.admin))],
)


@router.get("", response_model=UserListResponse, summary="[Admin] Danh sách và tìm kiếm người dùng")
def api_get_users(
    search: str | None = Query(None, description="Tìm theo email"),
    role: Role | None = Query(None, description="Lọc theo vai trò (student, employer, admin)"),
    is_locked: bool | None = Query(None, description="Lọc theo trạng thái khóa (true/false)"),
    page: int = Query(1, ge=1, description="Số trang (bắt đầu từ 1)"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Admin xem danh sách toàn bộ người dùng, tìm kiếm theo email và lọc theo vai trò/trạng thái."""
    return get_users_list(db, search, role, is_locked, page, limit)


@router.get("/{user_id}", response_model=UserDetailResponse, summary="[Admin] Xem chi tiết một người dùng")
def api_get_user_detail(
    user_id: int,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Admin xem chi tiết thông tin một tài khoản kèm theo hồ sơ sinh viên/doanh nghiệp."""
    return get_user_detail(db, user_id)


@router.patch("/{user_id}/status", response_model=UserDetailResponse, summary="[Admin] Khóa hoặc mở khóa tài khoản")
def api_update_user_lock_status(
    user_id: int,
    payload: UserStatusUpdateSchema,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Admin khóa hoặc mở khóa tài khoản. Tài khoản bị khóa sẽ không thể đăng nhập hoặc dùng token."""
    return update_user_lock_status(db, admin, user_id, payload)