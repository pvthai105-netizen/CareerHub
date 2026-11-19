from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Role


class UserSummaryResponse(BaseModel):
    """Thông tin tóm tắt của user trong danh sách quản trị."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    is_locked: bool
    created_at: datetime
    display_name: Optional[str] = None


class UserListResponse(BaseModel):
    """Dữ liệu trả về phân trang danh sách user."""
    total: int
    page: int
    limit: int
    items: list[UserSummaryResponse]


class UserStatusUpdateSchema(BaseModel):
    """Payload khóa / mở khóa tài khoản."""
    is_locked: bool = Field(..., description="True: Khóa tài khoản, False: Mở khóa")


class UserDetailResponse(BaseModel):
    """Thông tin chi tiết của 1 user kèm profile liên kết."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    is_locked: bool
    created_at: datetime
    student_profile: Optional[dict[str, Any]] = None
    employer_profile: Optional[dict[str, Any]] = None