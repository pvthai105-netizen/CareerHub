from datetime import date, datetime, timedelta, timezone
from typing import Dict, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.applications import Application, ApplicationStatus
from app.models.employee_profiles import EmployerProfile
from app.models.job import Job
from app.models.saved_jobs import SavedJob
from app.models.student_profiles import StudentProfile
from app.models.user import Role, User
from app.schemas.dashboard import (
    AdminDashboardResponse,
    AdminJobStats,
    AdminUserStats,
    DateCountItem,
    EmployerDashboardResponse,
    EmployerKpi,
    JobApplicationStatItem,
    RecentActivityItem,
    RecentApplicantItem,
    StudentApplicationItem,
    StudentSavedJobItem,
    StudentDashboardResponse,
    StudentSummary,
)


# ==============================================================================
# 1. THỐNG KÊ DASHBOARD CHO SINH VIÊN
# ==============================================================================
def get_student_dashboard_data(db: Session, current_user: User) -> StudentDashboardResponse:
    # 1. Tổng số đơn đã ứng tuyển
    applied_count = (
        db.query(func.count(Application.id))
        .filter(Application.student_id == current_user.id)
        .scalar()
        or 0
    )

    # 2. Tổng số tin việc làm đã lưu
    saved_count = (
        db.query(func.count(SavedJob.saved_job_id))
        .filter(SavedJob.user_id == current_user.id)
        .scalar()
        or 0
    )

    # 3. Thống kê số lượng đơn theo từng trạng thái bằng GROUP BY
    raw_statuses = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.student_id == current_user.id)
        .group_by(Application.status)
        .all()
    )

    status_dist: Dict[str, int] = {
        "pending": 0,
        "reviewed": 0,
        "interview": 0,
        "accepted": 0,
        "rejected": 0,
    }
    for st_val, count in raw_statuses:
        key = st_val.value if hasattr(st_val, "value") else str(st_val)
        status_dist[key] = count

    # 4. Danh sách các đơn ứng tuyển gần nhất (kèm tên công ty và công việc)
    recent_rows = (
        db.query(
            Application.id.label("application_id"),
            Job.job_id.label("job_id"),
            Job.title.label("job_title"),
            EmployerProfile.company_name.label("company_name"),
            Application.applied_at.label("applied_at"),
            Application.status.label("status"),
        )
        .join(Job, Application.job_id == Job.job_id)
        .outerjoin(EmployerProfile, Job.employer_id == EmployerProfile.user_id)
        .filter(Application.student_id == current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(10)
        .all()
    )

    recent_apps: List[StudentApplicationItem] = []
    for r in recent_rows:
        status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
        recent_apps.append(
            StudentApplicationItem(
                application_id=r.application_id,
                job_id=r.job_id,
                job_title=r.job_title,
                company_name=r.company_name or "Nhà tuyển dụng",
                applied_at=r.applied_at,
                status=status_str,
            )
        )

    # 5. Danh sách các tin việc làm đã lưu (kèm tên công ty và chi tiết công việc)
    saved_rows = (
        db.query(
            SavedJob.saved_job_id.label("saved_job_id"),
            Job.job_id.label("job_id"),
            Job.title.label("job_title"),
            EmployerProfile.company_name.label("company_name"),
            SavedJob.saved_at.label("saved_at"),
            Job.status.label("status"),
            Job.location.label("location"),
            Job.salary_min.label("salary_min"),
            Job.salary_max.label("salary_max"),
        )
        .join(Job, SavedJob.job_id == Job.job_id)
        .outerjoin(EmployerProfile, Job.employer_id == EmployerProfile.user_id)
        .filter(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.saved_at.desc())
        .all()
    )

    saved_jobs_list: List[StudentSavedJobItem] = []
    for s in saved_rows:
        job_st_str = s.status.value if hasattr(s.status, "value") else str(s.status or "ACTIVE")
        salary_str = None
        if s.salary_min and s.salary_max:
            salary_str = f"{int(s.salary_min / 1_000_000)} - {int(s.salary_max / 1_000_000)} triệu"
        elif s.salary_min:
            salary_str = f"Từ {int(s.salary_min / 1_000_000)} triệu"
        elif s.salary_max:
            salary_str = f"Đến {int(s.salary_max / 1_000_000)} triệu"

        saved_jobs_list.append(
            StudentSavedJobItem(
                saved_job_id=s.saved_job_id,
                job_id=s.job_id,
                job_title=s.job_title,
                company_name=s.company_name or "Nhà tuyển dụng",
                saved_at=s.saved_at,
                status=job_st_str,
                location=s.location or "",
                salary=salary_str or "Thỏa thuận",
            )
        )

    return StudentDashboardResponse(
        summary=StudentSummary(
            applied_count=applied_count,
            saved_count=saved_count,
            viewed_count=0,
        ),
        status_distribution=status_dist,
        recent_applications=recent_apps,
        saved_jobs=saved_jobs_list,
    )


# ==============================================================================
# 2. THỐNG KÊ DASHBOARD CHO NHÀ TUYỂN DỤNG
# ==============================================================================
def get_employer_dashboard_data(db: Session, current_user: User) -> EmployerDashboardResponse:
    # 1. Thẻ KPI
    total_jobs = (
        db.query(func.count(Job.job_id))
        .filter(Job.employer_id == current_user.id)
        .scalar()
        or 0
    )

    active_jobs = (
        db.query(func.count(Job.job_id))
        .filter(Job.employer_id == current_user.id, Job.status == "ACTIVE")
        .scalar()
        or 0
    )

    total_applicants = (
        db.query(func.count(Application.id))
        .join(Job, Application.job_id == Job.job_id)
        .filter(Job.employer_id == current_user.id)
        .scalar()
        or 0
    )

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_applicants_7d = (
        db.query(func.count(Application.id))
        .join(Job, Application.job_id == Job.job_id)
        .filter(
            Job.employer_id == current_user.id,
            Application.applied_at >= seven_days_ago,
        )
        .scalar()
        or 0
    )

    # 2. GROUP BY: Lượt ứng tuyển theo từng tin tuyển dụng
    jobs_stat_raw = (
        db.query(
            Job.job_id,
            Job.title,
            Job.status,
            func.count(Application.id).label("total_applications"),
        )
        .outerjoin(Application, Job.job_id == Application.job_id)
        .filter(Job.employer_id == current_user.id)
        .group_by(Job.job_id, Job.title, Job.status)
        .order_by(func.count(Application.id).desc())
        .all()
    )

    applications_by_job = [
        JobApplicationStatItem(
            job_id=row.job_id,
            title=row.title,
            status=row.status,
            total_applications=row.total_applications,
        )
        for row in jobs_stat_raw
    ]

    # 3. GROUP BY: Lượt ứng tuyển theo 7 ngày gần nhất (cho biểu đồ cột)
    today = date.today()
    date_list = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    date_strings = [d.strftime("%Y-%m-%d") for d in date_list]

    min_start_datetime = datetime.combine(date_list[0], datetime.min.time())
    daily_apps_raw = (
        db.query(
            func.date(Application.applied_at).label("app_date"),
            func.count(Application.id).label("count"),
        )
        .join(Job, Application.job_id == Job.job_id)
        .filter(
            Job.employer_id == current_user.id,
            Application.applied_at >= min_start_datetime,
        )
        .group_by(func.date(Application.applied_at))
        .all()
    )

    daily_dict = {str(row.app_date): row.count for row in daily_apps_raw}
    applications_by_date = [
        DateCountItem(date=d_str, count=daily_dict.get(d_str, 0))
        for d_str in date_strings
    ]

    # 4. GROUP BY: Trạng thái ứng viên và % tương ứng (cho thanh tiến độ)
    status_raw = (
        db.query(Application.status, func.count(Application.id))
        .join(Job, Application.job_id == Job.job_id)
        .filter(Job.employer_id == current_user.id)
        .group_by(Application.status)
        .all()
    )

    status_dist: Dict[str, int] = {
        "pending": 0,
        "reviewed": 0,
        "interview": 0,
        "accepted": 0,
        "rejected": 0,
    }
    for st_val, count in status_raw:
        key = st_val.value if hasattr(st_val, "value") else str(st_val)
        status_dist[key] = count

    status_percentages: Dict[str, float] = {}
    for k, v in status_dist.items():
        pct = round((v / total_applicants * 100), 1) if total_applicants > 0 else 0.0
        status_percentages[k] = pct

    # 5. Danh sách ứng viên mới nhất
    recent_apps_raw = (
        db.query(
            Application.id.label("application_id"),
            StudentProfile.full_name.label("student_name"),
            Job.title.label("job_title"),
            Application.applied_at.label("applied_at"),
            Application.status.label("status"),
        )
        .join(Job, Application.job_id == Job.job_id)
        .outerjoin(StudentProfile, Application.student_id == StudentProfile.user_id)
        .filter(Job.employer_id == current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(6)
        .all()
    )

    recent_applicants = [
        RecentApplicantItem(
            application_id=row.application_id,
            student_name=row.student_name or "Ứng viên ẩn danh",
            job_title=row.job_title,
            applied_at=row.applied_at,
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
        )
        for row in recent_apps_raw
    ]

    return EmployerDashboardResponse(
        kpi=EmployerKpi(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            total_applicants=total_applicants,
            new_applicants_7d=new_applicants_7d,
        ),
        applications_by_job=applications_by_job,
        applications_by_date=applications_by_date,
        status_distribution=status_dist,
        status_percentages=status_percentages,
        recent_applicants=recent_applicants,
    )


# ==============================================================================
# 3. THỐNG KÊ DASHBOARD TOÀN HỆ THỐNG CHO ADMIN
# ==============================================================================
def get_admin_dashboard_data(db: Session, current_user: User) -> AdminDashboardResponse:
    # 1. GROUP BY: Tổng người dùng phân theo vai trò
    roles_raw = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    user_map = {"student": 0, "employer": 0, "admin": 0}
    total_users = 0
    for r_val, count in roles_raw:
        key = r_val.value if hasattr(r_val, "value") else str(r_val)
        user_map[key] = count
        total_users += count

    user_stats = AdminUserStats(
        total_users=total_users,
        students_count=user_map.get("student", 0),
        employers_count=user_map.get("employer", 0),
        admins_count=user_map.get("admin", 0),
    )

    # 2. GROUP BY: Tổng tin tuyển dụng phân theo trạng thái
    jobs_raw = db.query(Job.status, func.count(Job.job_id)).group_by(Job.status).all()
    job_map: Dict[str, int] = {}
    total_jobs = 0
    for st_val, count in jobs_raw:
        key = st_val.upper() if isinstance(st_val, str) else str(st_val)
        job_map[key] = count
        total_jobs += count

    job_stats = AdminJobStats(
        total_jobs=total_jobs,
        active_jobs=job_map.get("ACTIVE", 0),
        closed_jobs=job_map.get("CLOSED", 0),
        draft_jobs=job_map.get("DRAFT", 0),
    )

    # 3. Tổng lượt ứng tuyển trên toàn hệ thống
    total_applications = db.query(func.count(Application.id)).scalar() or 0

    # 4. GROUP BY: Tin tuyển dụng mới theo ngày (7 ngày gần nhất)
    today = date.today()
    date_list = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    date_strings = [d.strftime("%Y-%m-%d") for d in date_list]

    min_start_datetime = datetime.combine(date_list[0], datetime.min.time())
    daily_jobs_raw = (
        db.query(
            func.date(Job.created_at).label("job_date"),
            func.count(Job.job_id).label("count"),
        )
        .filter(Job.created_at >= min_start_datetime)
        .group_by(func.date(Job.created_at))
        .all()
    )

    daily_jobs_dict = {str(row.job_date): row.count for row in daily_jobs_raw}
    jobs_by_date = [
        DateCountItem(date=d_str, count=daily_jobs_dict.get(d_str, 0))
        for d_str in date_strings
    ]

    # 5. GROUP BY: Tăng trưởng người dùng mới theo tháng (6 tháng gần nhất cho MySQL)
    month_expr = func.date_format(User.created_at, "%Y-%m")

    user_growth_raw = (
        db.query(
            month_expr.label("month"),
            func.count(User.id).label("count"),
        )
        .group_by(month_expr)
        .order_by("month")
        .limit(6)
        .all()
    )

    user_growth = [
        DateCountItem(date=str(row.month), count=row.count)
        for row in user_growth_raw
    ]

    # 6. Hoạt động gần đây của hệ thống
    recent_jobs = (
        db.query(Job.title, Job.created_at, EmployerProfile.company_name)
        .outerjoin(EmployerProfile, Job.employer_id == EmployerProfile.user_id)
        .order_by(Job.created_at.desc())
        .limit(5)
        .all()
    )

    recent_activities: List[RecentActivityItem] = []
    for j in recent_jobs:
        c_name = j.company_name or "Doanh nghiệp"
        recent_activities.append(
            RecentActivityItem(
                title=f"{c_name} đăng tin tuyển dụng '{j.title}'",
                created_at=j.created_at,
                activity_type="job_post",
            )
        )

    return AdminDashboardResponse(
        user_stats=user_stats,
        job_stats=job_stats,
        total_applications=total_applications,
        jobs_by_date=jobs_by_date,
        user_growth=user_growth,
        recent_activities=recent_activities,
    )
