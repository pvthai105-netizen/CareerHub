import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.student_profiles import DesiredJobType


# Schema cập nhật thông tin hồ sơ 
class StudentProfileUpdateSchema(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="Họ và tên sinh viên")
    phone: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    university: Optional[str] = Field(None, max_length=150, description="Tên trường đại học")
    major: Optional[str] = Field(None, max_length=100, description="Chuyên ngành")
    bio: Optional[str] = Field(None, description="Giới thiệu bản thân")
    skills: Optional[str] = Field(None, description="Danh sách kỹ năng")
    desired_job_type: Optional[DesiredJobType] = Field(None, description="Loại công việc mong muốn")
    avatar_url: Optional[str] = Field(None, max_length=255, description="URL ảnh đại diện")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Họ và tên không được để trống hoặc chỉ chứa khoảng trắng.")
            if len(v) > 100:
                raise ValueError("Họ và tên không được dài quá 100 ký tự.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v:
                if not re.match(r"^(0|\+84)[0-9]{9}$", v):
                    raise ValueError("Số điện thoại không hợp lệ (cần 10 chữ số, ví dụ: 0901234567 hoặc +84901234567).")
            else:
                return None
        return v

    @field_validator("university", "major", "bio", "skills", "avatar_url")
    @classmethod
    def strip_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None


# Schema dữ liệu trả về
class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    desired_job_type: DesiredJobType
    avatar_url: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)