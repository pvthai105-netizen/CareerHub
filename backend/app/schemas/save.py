from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict

# Thông tin chi tiết tin tuyển dụng.
class SavedJobDetailResponse(BaseModel):
    job_id: int
    title: str
    description: str
    industry: str
    location: str
    salary_min: float
    salary_max: float
    job_type: str
    deadline: datetime | None = None
    status: str
    company_name: str = ""          # ên công ty hiển thị ở tab Đã lưu

    model_config = ConfigDict(from_attributes=True)


# Thông tin tin tuyển dụng đã lưu.
class SavedJobResponse(BaseModel):
    saved_job_id: int
    user_id: int
    job_id: int
    saved_at: datetime

    # Lấy thông tin Job thông qua relationship
    job: SavedJobDetailResponse

    model_config = ConfigDict(from_attributes=True) # Cho phép Pydantic đọc dữ liệu trực tiếp từ SQLAlchemy Model


class SavedJobCheckResponse(BaseModel):
    """Kết quả kiểm tra một tin đã được lưu hay chưa"""
    is_saved: bool = Field(..., description="True nếu sinh viên đã lưu tin này")