from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Literal
from sqlalchemy.orm import Session
from app import deps
from app.models.job import JobType, JobStatus
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
)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    dependencies=[Depends(deps.require_roles(deps.Role.employer))],
)


# Tạo tin tuyển dụng
@router.post("", response_model=JobBaseSchema, status_code=status.HTTP_201_CREATED)
def api_create_job(
    payload: JobCreateSchema,
    db: Session = Depends(deps.get_db),
    employer=Depends(deps.get_current_user),
):
    return create_job(db, employer, payload)


# Danh sách tin của mình
@router.get("/my-jobs", response_model=JobListResponse)
def api_my_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    job_status: JobStatus | None = Query(None),
    db: Session = Depends(deps.get_db),
    employer=Depends(deps.get_current_user),
):
    return get_my_jobs(db, employer, skip, limit, job_status)


# Chi tiết tin của mình
@router.get("/my-jobs/{job_id}", response_model=JobBaseSchema)
def api_my_job_detail(job_id: int, db: Session = Depends(deps.get_db), employer=Depends(deps.get_current_user),):
    return get_my_job(db, employer, job_id)


# Cập nhật tin
@router.put("/my-jobs/{job_id}", response_model=JobBaseSchema)
def api_update_job(job_id: int, payload: JobUpdateSchema,db: Session = Depends(deps.get_db), employer=Depends(deps.get_current_user),):
    return update_job(db, employer, job_id, payload)


# Xóa tin
@router.delete("/my-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_job(job_id: int, db: Session = Depends(deps.get_db), employer=Depends(deps.get_current_user)):
    delete_job(db, employer, job_id)
    return None


@router.patch("/{job_id}/status", response_model=JobBaseSchema)
def api_change_status(
    job_id: int,
    payload: JobStatusPatchSchema,
    db: Session = Depends(deps.get_db),
    employer=Depends(deps.get_current_user),
):
    return change_status(db, employer, job_id, payload)