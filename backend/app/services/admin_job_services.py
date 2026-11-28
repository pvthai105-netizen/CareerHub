from datetime import date, datetime
from math import ceil
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.job import Job, JobStatus
from app.models.user import User
from app.models.employee_profiles import EmployerProfile
from app.schemas.admin_job import (
    AdminJobDetailResponse,
    AdminJobItemSchema,
    AdminJobListResponse,
    AdminJobStatusUpdateSchema,
)


def _format_job_item(job: Job) -> AdminJobItemSchema:
    """Helper chuyển đổi Job ORM sang Schema kèm tên công ty."""
    company_name = None
    employer_email = None
    if job.employer:
        employer_email = job.employer.email
        if job.employer.employer_profile:
            company_name = job.employer.employer_profile.company_name

    return AdminJobItemSchema(
        job_id=job.job_id,
        title=job.title,
        industry=job.industry,
        location=job.location,
        salary_min=float(job.salary_min) if job.salary_min is not None else None,
        salary_max=float(job.salary_max) if job.salary_max is not None else None,
        job_type=job.job_type,
        deadline=job.deadline,
        status=JobStatus(job.status),
        employer_id=job.employer_id,
        company_name=company_name,
        employer_email=employer_email,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def get_admin_jobs(
    db: Session,
    status_filter: JobStatus | None = None,
    keyword: str | None = None,
    page: int = 1,
    limit: int = 10,
) -> AdminJobListResponse:
    """Admin tra cứu danh sách tin, lọc theo trạng thái (chờ duyệt, đã duyệt, bị ẩn)."""
    if page < 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Số trang phải >= 1.")
    if not (1 <= limit <= 100):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Số lượng tin mỗi trang phải từ 1 đến 100.")

    query = db.query(Job)

    # 1. Lọc theo trạng thái tin (Ví dụ: DRAFT để xem tin chờ duyệt)
    if status_filter:
        query = query.filter(Job.status == status_filter.value)

    # 2. Tìm kiếm theo tiêu đề hoặc ngành nghề
    if keyword and keyword.strip():
        kw = f"%{keyword.strip().lower()}%"
        query = query.filter(
            (Job.title.ilike(kw)) | (Job.industry.ilike(kw)) | (Job.location.ilike(kw))
        )

    total = query.count()
    total_pages = ceil(total / limit) if total else 0
    offset = (page - 1) * limit
    jobs = (
        query.options(
            joinedload(Job.employer).joinedload(User.employer_profile)
        )
        .order_by(Job.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = [_format_job_item(j) for j in jobs]

    return AdminJobListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        items=items,
    )


def get_admin_job_detail(db: Session, job_id: int) -> AdminJobDetailResponse:
    """Admin xem chi tiết đầy đủ của một tin tuyển dụng."""
    job = (
        db.query(Job)
        .options(
            joinedload(Job.employer).joinedload(User.employer_profile)
        )
        .filter(Job.job_id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tin tuyển dụng với ID này.",
        )

    company_name = None
    company_website = None
    contact_phone = None
    employer_email = None

    if job.employer:
        employer_email = job.employer.email
        if job.employer.employer_profile:
            ep = job.employer.employer_profile
            company_name = ep.company_name
            company_website = ep.company_website
            contact_phone = ep.phone

    return AdminJobDetailResponse(
        job_id=job.job_id,
        title=job.title,
        description=job.description,
        industry=job.industry,
        location=job.location,
        salary_min=float(job.salary_min) if job.salary_min is not None else None,
        salary_max=float(job.salary_max) if job.salary_max is not None else None,
        job_type=job.job_type,
        deadline=job.deadline,
        status=JobStatus(job.status),
        employer_id=job.employer_id,
        company_name=company_name,
        company_website=company_website,
        employer_email=employer_email,
        contact_phone=contact_phone,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def update_job_status_by_admin(
    db: Session,
    job_id: int,
    new_status: JobStatus,
) -> AdminJobDetailResponse:
    """Admin cập nhật trạng thái tin (Duyệt tin ACTIVE, hoặc Ẩn tin PAUSED)."""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tin tuyển dụng với ID này.",
        )

    # Ràng buộc: Không duyệt tin đã quá hạn nộp hồ sơ
    if new_status == JobStatus.ACTIVE and job.deadline < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể duyệt tin khi hạn nộp hồ sơ (deadline) đã qua.",
        )

    job.status = new_status.value
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    return get_admin_job_detail(db, job_id)