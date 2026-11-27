from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Literal
from sqlalchemy.orm import Session
from app import deps
from app.models.job import JobType, JobStatus
from app.models.user import Role, User
from app.schemas.job import (
    JobCreateSchema,
    JobListResponse,
    JobBaseSchema,
    JobUpdateSchema,
    JobStatusPatchSchema,
)
from app.services.job_services import (
    create_job,
    get_my_jobs,
    get_my_job,
    update_job,
    delete_job,
    change_status,
    get_public_jobs,
)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    # No global dependency; each endpoint adds its own role requirement.
)


# Tạo tin tuyển dụng
@router.post("", response_model=JobBaseSchema, status_code=status.HTTP_201_CREATED, summary="Tạo tin mới")
def api_create_job(
    payload: JobCreateSchema,
    db: Session = Depends(deps.get_db),
    employer: User = Depends(deps.require_roles(Role.employer)),
):
    return create_job(db, employer, payload)


# Danh sách tin của mình
@router.get("/my-jobs", response_model=JobListResponse, summary="Lấy danh sách tin của mình")
def api_my_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    job_status: JobStatus | None = Query(None),
    db: Session = Depends(deps.get_db),
    employer: User = Depends(deps.require_roles(Role.employer)),
):
    return get_my_jobs(db, employer, skip, limit, job_status)


# Chi tiết tin của mình
@router.get("/my-jobs/{job_id}", response_model=JobBaseSchema, summary="Lấy chi tiết tin của mình")
def api_my_job_detail(
    job_id: int,
    db: Session = Depends(deps.get_db),
    employer: User = Depends(deps.require_roles(Role.employer)),
):
    return get_my_job(db, employer, job_id)


# Cập nhật tin
@router.put("/my-jobs/{job_id}", response_model=JobBaseSchema, summary="Cập nhật tin")
def api_update_job(
    job_id: int,
    payload: JobUpdateSchema,
    db: Session = Depends(deps.get_db),
    employer: User = Depends(deps.require_roles(Role.employer)),
):
    return update_job(db, employer, job_id, payload)


# Xóa tin
@router.delete("/my-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa tin")
def api_delete_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    employer: User = Depends(deps.require_roles(Role.employer)),
):
    delete_job(db, employer, job_id)
    return None


@router.patch("/{job_id}/status", response_model=JobBaseSchema, summary="Cập nhật trạng thái tin")
def api_change_status(
    job_id: int,
    payload: JobStatusPatchSchema,
    db: Session = Depends(deps.get_db),
    employer: User = Depends(deps.require_roles(Role.employer)),
):
    return change_status(db, employer, job_id, payload)


@router.get("/", response_model=JobListResponse, summary="Danh sách tin tuyển dụng công khai")
def api_public_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    industry: str | None = Query(None),
    location: str | None = Query(None),
    min_salary: float | None = Query(None, ge=0),
    max_salary: float | None = Query(None, ge=0),
    job_type: JobType | None = Query(None),
    db: Session = Depends(deps.get_db),
):
    return get_public_jobs(
        db,
        page=page,
        limit=limit,
        keyword=keyword,
        industry=industry,
        location=location,
        min_salary=min_salary,
        max_salary=max_salary,
        job_type=job_type,
    )