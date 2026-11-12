from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    # bcrypt chỉ xử lý tối đa 72 byte nên giới hạn 64 ký tự cho an toàn
    password: str = Field(min_length=8, max_length=64)
    # Chỉ cho tự đăng ký Student hoặc Employer, KHÔNG cho tự đăng ký admin
    role: Literal["student", "employer"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    is_locked: bool