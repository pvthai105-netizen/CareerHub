import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps import get_current_user, get_db
from app.schemas.save import SavedJobResponse, SavedJobCheckResponse
from app.services.save_services import (
    add_saved_job,
    remove_saved_job,
    list_saved_jobs,
    is_job_saved,
)


# Tạo logger để ghi nhận lỗi.
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user/saved-jobs",
    tags=["Saved Jobs"]
)


@router.post("/{job_id}", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
def save_job(
    job_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return add_saved_job(db, user.id, job_id)


@router.delete("/{job_id}", response_model=SavedJobResponse)
def unsave_job(
    job_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return remove_saved_job(db, user.id, job_id)


@router.get("", response_model=list[SavedJobResponse])
def get_saved_jobs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return list_saved_jobs(db, user.id, skip=skip, limit=limit)


@router.get("/{job_id}/check", response_model=SavedJobCheckResponse)
def check_saved_job(
    job_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    saved = is_job_saved(db, user.id, job_id)
    return SavedJobCheckResponse(is_saved=saved)