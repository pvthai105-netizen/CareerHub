import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# 1. Schema cập nhật thông tin hồ sơ công ty
class EmployerProfileUpdateSchema(BaseModel):
    company_name: Optional[str] = Field(None, max_length=200, description="Tên công ty / doanh nghiệp")
    contact_name: Optional[str] = Field(None, max_length=100, description="Họ và tên người đại diện / liên hệ")
    phone: Optional[str] = Field(None, max_length=20, description="Số điện thoại liên hệ")
    company_website: Optional[str] = Field(None, max_length=255, description="Website công ty")
    address: Optional[str] = Field(None, max_length=255, description="Địa chỉ trụ sở công ty")
    description: Optional[str] = Field(None, description="Mô tả / giới thiệu công ty")
    tax_code: Optional[str] = Field(None, max_length=50, description="Mã số thuế doanh nghiệp")
    logo_url: Optional[str] = Field(None, max_length=255, description="URL đường dẫn logo công ty")

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tên công ty không được để trống hoặc chỉ chứa khoảng trắng.")
            if len(v) > 200:
                raise ValueError("Tên công ty không được dài quá 200 ký tự.")
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

    @field_validator("contact_name", "company_website", "address", "description", "tax_code", "logo_url")
    @classmethod
    def strip_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None


# 2. Schema tạo mới hồ sơ công ty
class EmployerProfileCreateSchema(EmployerProfileUpdateSchema):
    company_name: str = Field(..., max_length=200, description="Tên công ty / doanh nghiệp (bắt buộc)")


# 3. Schema dữ liệu trả về cho client
class EmployerProfileResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    company_website: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    tax_code: Optional[str] = None
    is_verified: bool = False
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# 4. Schema phản hồi khi upload logo thành công
class LogoUploadResponse(BaseModel):
    message: str = "Upload logo thành công"
    logo_url: str
    file_name: str
    file_size_kb: float