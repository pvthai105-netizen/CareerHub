import logging
from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.saved_jobs import SavedJob
from app.models.job import Job


# Tạo logger để ghi nhận lỗi.
logger = logging.getLogger(__name__)


def add_saved_job(db: Session, user_id: int, job_id: int) -> SavedJob:
    # Tìm tin tuyển dụng theo job_id
    job = db.query(Job).filter(Job.job_id == job_id).first()

    # Nếu không tìm thấy tin thì trả về lỗi 404.
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tin tuyển dụng."
        )

    # Kiểm tra người dùng đã lưu tin này chưa.
    existing_saved = (
        db.query(SavedJob).filter(SavedJob.user_id == user_id, SavedJob.job_id == job_id).first()
    )

    # Nếu đã lưu thì không cho phép lưu trùng.
    if existing_saved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bạn đã lưu tin tuyển dụng này rồi."
        )

    # Tạo bản ghi lưu tin mới.
    saved = SavedJob(
        user_id=user_id,
        job_id=job_id
    )

    try:
        # Thêm bản ghi vào Database.
        db.add(saved)

        # Lưu dữ liệu.
        db.commit()

        # Cập nhật dữ liệu vừa lưu.
        db.refresh(saved)

        # Tải thông tin Job thông qua relationship.
        saved = (
            db.query(SavedJob)
            .options(joinedload(SavedJob.job))
            .filter(SavedJob.saved_job_id == saved.saved_job_id)
            .first()
        )

        # Trả về Model để FastAPI chuyển thành Schema.
        return saved

    except IntegrityError:
        # Hoàn tác nếu xảy ra lỗi dữ liệu trùng.
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tin tuyển dụng này đã được lưu trước đó."
        )

    except Exception as errors:
        # Hoàn tác nếu xảy ra lỗi.
        db.rollback()

        logger.exception("Lỗi khi bỏ lưu tin tuyển dụng.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(errors)
        )


def remove_saved_job(db: Session, user_id: int, job_id: int) -> SavedJob:
    # Tìm bản ghi đã lưu và tải thông tin Job đi kèm.
    saved = (
        db.query(SavedJob)
        .options(joinedload(SavedJob.job))
        .filter(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id
        )
        .first()
    )

    # Nếu chưa lưu tin thì trả về lỗi 404.
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bạn chưa lưu tin tuyển dụng này."
        )

    try:
        # Xóa bản ghi lưu tin.
        db.delete(saved)

        # Lưu thay đổi vào Database.
        db.commit()

        # Trả về bản ghi vừa bỏ lưu.
        return saved

    except Exception as errors:
        # Hoàn tác nếu xảy ra lỗi.
        db.rollback()

        logger.exception("Lỗi khi bỏ lưu tin tuyển dụng.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(errors)
        )


def list_saved_jobs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[SavedJob]:

    # Lấy danh sách tin đã lưu và tải thông tin Job đi kèm.
    saved_jobs = (
        db.query(SavedJob)
        .options(joinedload(SavedJob.job))
        .filter(SavedJob.user_id == user_id)
        .order_by(SavedJob.saved_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Trả về danh sách Model.
    return saved_jobs


def is_job_saved(db: Session, user_id: int, job_id: int) -> bool:

    # Tìm bản ghi theo người dùng và tin tuyển dụng.
    saved = (
        db.query(SavedJob)
        .filter(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id
        )
        .first()
    )

    return saved is not None # Có bản ghi thì trả về True, ngược lại False