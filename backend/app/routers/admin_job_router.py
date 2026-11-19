from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import deps
from app.models.job import JobStatus
from app.models.user import Role, User
from app.schemas.admin_job import (
    AdminJobDetailResponse,
    AdminJobListResponse,
    AdminJobStatusUpdateSchema,
)
from app.services.admin_job_services import (
    get_admin_job_detail,
    get_admin_jobs,
    update_job_status_by_admin,
)

router = APIRouter(
    prefix="/api/admin/jobs",
    tags=["admin-jobs"],
    # Yêu cầu bắt buộc quyền ADMIN cho toàn bộ endpoints
    dependencies=[Depends(deps.require_roles(Role.admin))],
)


@router.get("", response_model=AdminJobListResponse, summary="[Admin] Danh sách và tìm kiếm tin tuyển dụng")
def api_get_admin_jobs(
    status: JobStatus | None = Query(None, description="Lọc trạng thái: DRAFT (chờ duyệt), ACTIVE (đã duyệt), PAUSED (bị ẩn)"),
    keyword: str | None = Query(None, description="Tìm theo tiêu đề, ngành nghề, địa điểm"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(10, ge=1, le=100, description="Số lượng mỗi trang"),
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Admin xem danh sách tin tuyển dụng. Để xem các tin chờ duyệt, truyền tham số status=DRAFT."""
    return get_admin_jobs(db, status_filter=status, keyword=keyword, page=page, limit=limit)


@router.get("/{job_id}", response_model=AdminJobDetailResponse, summary="[Admin] Xem chi tiết tin tuyển dụng")
def api_get_admin_job_detail(
    job_id: int,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Admin xem nội dung chi tiết của một tin tuyển dụng cần kiểm duyệt."""
    return get_admin_job_detail(db, job_id)


@router.patch("/{job_id}/status", response_model=AdminJobDetailResponse, summary="[Admin] Cập nhật trạng thái tin")
def api_update_job_status(
    job_id: int,
    payload: AdminJobStatusUpdateSchema,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Admin duyệt hoặc ẩn tin bằng cách thay đổi status (ACTIVE: duyệt, PAUSED: ẩn tin)."""
    return update_job_status_by_admin(db, job_id, payload.status)


@router.post("/{job_id}/approve", response_model=AdminJobDetailResponse, summary="[Admin] Phê duyệt tin tuyển dụng")
def api_approve_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Endpoint nhanh: Phê duyệt tin tuyển dụng (chuyển sang ACTIVE để xuất hiện công khai)."""
    return update_job_status_by_admin(db, job_id, JobStatus.ACTIVE)


@router.post("/{job_id}/hide", response_model=AdminJobDetailResponse, summary="[Admin] Ẩn tin tuyển dụng")
def api_hide_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_user),
):
    """Endpoint nhanh: Ẩn tin tuyển dụng (chuyển sang PAUSED để không hiển thị công khai)."""
    return update_job_status_by_admin(db, job_id, JobStatus.PAUSED)