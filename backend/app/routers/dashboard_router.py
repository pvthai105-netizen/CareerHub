from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import deps
from app.models.user import Role, User
from app.schemas.dashboard import (
    AdminDashboardResponse,
    EmployerDashboardResponse,
    StudentDashboardResponse,
)
from app.services.dashboard_services import (
    get_admin_dashboard_data,
    get_employer_dashboard_data,
    get_student_dashboard_data,
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)


@router.get(
    "/student",
    response_model=StudentDashboardResponse,
    summary="Thống kê dashboard cho sinh viên",
)
def api_get_student_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    """
    Lấy dữ liệu của chính sinh viên đang đăng nhập và thống kê đơn ứng tuyển:
    - Tổng đơn đã ứng tuyển, việc làm đã lưu.
    - Thống kê đơn theo trạng thái (GROUP BY: pending, reviewed, interview, accepted, rejected).
    - Danh sách đơn ứng tuyển gần nhất kèm tên việc làm và công ty.
    """
    return get_student_dashboard_data(db, current_user)


@router.get(
    "/employer",
    response_model=EmployerDashboardResponse,
    summary="Thống kê dashboard cho nhà tuyển dụng",
)
def api_get_employer_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.employer)),
):
    """
    Lấy dữ liệu thống kê cho doanh nghiệp đang đăng nhập:
    - Thẻ KPI: Tổng tin, tin active, tổng ứng viên, ứng viên mới 7 ngày.
    - GROUP BY lượt ứng tuyển theo từng tin tuyển dụng.
    - GROUP BY lượt ứng tuyển theo 7 ngày gần nhất (phục vụ biểu đồ cột Chart.js).
    - Tỷ lệ % trạng thái ứng viên (cho thanh tiến độ).
    - Danh sách ứng viên mới nhất.
    """
    return get_employer_dashboard_data(db, current_user)


@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    summary="Thống kê dashboard toàn hệ thống cho admin",
)
def api_get_admin_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.admin)),
):
    """
    Lấy dữ liệu thống kê tổng thể toàn hệ thống cho admin:
    - GROUP BY tổng người dùng (tổng user, sinh viên, doanh nghiệp, admin).
    - GROUP BY tổng tin tuyển dụng theo trạng thái (active, closed, draft).
    - Tổng lượt ứng tuyển trên toàn hệ thống.
    - GROUP BY tin mới theo ngày (7 ngày gần nhất cho Chart.js).
    - GROUP BY tăng trưởng người dùng mới theo tháng.
    - Danh sách hoạt động gần đây của hệ thống.
    """
    return get_admin_dashboard_data(db, current_user)
