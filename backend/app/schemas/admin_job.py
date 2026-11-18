from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.job import JobStatus, JobType


class AdminJobItemSchema(BaseModel):
    """Thông tin tóm tắt tin tuyển dụng hiển thị cho Admin."""
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    title: str
    industry: str
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: str
    deadline: date
    status: JobStatus
    employer_id: int
    company_name: Optional[str] = None
    employer_email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminJobListResponse(BaseModel):
    """Phản hồi danh sách tin phân trang cho Admin."""
    total: int
    page: int
    limit: int
    total_pages: int
    items: list[AdminJobItemSchema]


class AdminJobDetailResponse(BaseModel):
    """Chi tiết tin tuyển dụng kèm hồ sơ công ty đầy đủ."""
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    title: str
    description: str
    industry: str
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: str
    deadline: date
    status: JobStatus
    employer_id: int
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    employer_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminJobStatusUpdateSchema(BaseModel):
    """Payload duyệt hoặc ẩn tin."""
    status: JobStatus = Field(
        ..., 
        description="Trạng thái duyệt mới: ACTIVE (Duyệt tin), PAUSED (Ẩn tin), CLOSED (Đóng tin)"
    )