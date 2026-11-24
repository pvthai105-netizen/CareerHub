from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DateCountItem(BaseModel):
    date: str = Field(..., description="Ngày hoặc tháng thống kê (YYYY-MM-DD hoặc YYYY-MM)")
    count: int = Field(..., description="Số lượng tương ứng")


# 1. SCHEMAS CHO SINH VIÊN
class StudentApplicationItem(BaseModel):
    application_id: int
    job_id: int
    job_title: str
    company_name: str
    applied_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class StudentSavedJobItem(BaseModel):
    saved_job_id: int
    job_id: int
    job_title: str
    company_name: str
    saved_at: datetime
    status: str = "ACTIVE"
    location: Optional[str] = None
    salary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentSummary(BaseModel):
    applied_count: int = Field(0, description="Tổng số đơn đã ứng tuyển")
    saved_count: int = Field(0, description="Tổng số tin việc làm đã lưu")
    viewed_count: int = Field(0, description="Tổng số tin việc làm đã xem")


class StudentDashboardResponse(BaseModel):
    summary: StudentSummary
    status_distribution: Dict[str, int] = Field(
        ...,
        description="Số lượng đơn theo từng trạng thái (pending, reviewed, interview, accepted, rejected)",
    )
    saved_jobs: List[StudentSavedJobItem] = Field(
        default_factory=list,
        description="Danh sách các công việc đã lưu của sinh viên",
    )
    recent_applications: List[StudentApplicationItem] = Field(
        default_factory=list,
        description="Danh sách các đơn ứng tuyển gần nhất",
    )


# ==========================================
# 2. SCHEMAS CHO NHÀ TUYỂN DỤNG
# ==========================================
class EmployerKpi(BaseModel):
    total_jobs: int = Field(0, description="Tổng số tin tuyển dụng")
    active_jobs: int = Field(0, description="Số tin đang hoạt động")
    total_applicants: int = Field(0, description="Tổng số ứng viên / lượt nộp")
    new_applicants_7d: int = Field(0, description="Số ứng viên mới nộp trong 7 ngày gần nhất")


class JobApplicationStatItem(BaseModel):
    job_id: int
    title: str
    status: str
    total_applications: int = Field(0, description="Tổng số lượt ứng tuyển vào tin này")


class RecentApplicantItem(BaseModel):
    application_id: int
    student_name: str
    job_title: str
    applied_at: datetime
    status: str


class EmployerDashboardResponse(BaseModel):
    kpi: EmployerKpi
    applications_by_job: List[JobApplicationStatItem] = Field(
        default_factory=list,
        description="Thống kê số lượt ứng tuyển theo từng tin tuyển dụng (GROUP BY)",
    )
    applications_by_date: List[DateCountItem] = Field(
        default_factory=list,
        description="Thống kê lượt ứng tuyển theo ngày trong 7 ngày gần nhất (cho biểu đồ cột)",
    )
    status_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Số lượng ứng viên phân theo trạng thái hồ sơ",
    )
    status_percentages: Dict[str, float] = Field(
        default_factory=dict,
        description="Tỷ lệ % ứng viên theo trạng thái (cho thanh tiến độ)",
    )
    recent_applicants: List[RecentApplicantItem] = Field(
        default_factory=list,
        description="Danh sách ứng viên nộp hồ sơ mới nhất",
    )


# ==========================================
# 3. SCHEMAS CHO QUẢN TRỊ VIÊN (ADMIN)
# ==========================================
class AdminUserStats(BaseModel):
    total_users: int = Field(0, description="Tổng số người dùng toàn hệ thống")
    students_count: int = Field(0, description="Số lượng sinh viên")
    employers_count: int = Field(0, description="Số lượng doanh nghiệp")
    admins_count: int = Field(0, description="Số lượng admin")


class AdminJobStats(BaseModel):
    total_jobs: int = Field(0, description="Tổng số tin tuyển dụng")
    active_jobs: int = Field(0, description="Số tin đang hoạt động")
    closed_jobs: int = Field(0, description="Số tin đã đóng")
    draft_jobs: int = Field(0, description="Số tin bản nháp")


class RecentActivityItem(BaseModel):
    title: str
    created_at: datetime
    activity_type: str


class AdminDashboardResponse(BaseModel):
    user_stats: AdminUserStats
    job_stats: AdminJobStats
    total_applications: int = Field(0, description="Tổng lượt ứng tuyển toàn hệ thống")
    jobs_by_date: List[DateCountItem] = Field(
        default_factory=list,
        description="Số lượng tin tuyển dụng mới theo từng ngày (GROUP BY)",
    )
    user_growth: List[DateCountItem] = Field(
        default_factory=list,
        description="Tăng trưởng người dùng mới theo tháng (GROUP BY)",
    )
    recent_activities: List[RecentActivityItem] = Field(
        default_factory=list,
        description="Danh sách hoạt động gần đây của hệ thống",
    )
