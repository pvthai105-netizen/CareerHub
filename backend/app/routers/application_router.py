from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app import deps
from app.models.user import Role, User
from app.schemas.application import ApplicationResponse, MyApplicationResponse
from app.services.application_services import (
    MAX_CV_SIZE,
    apply_to_job,
    get_my_applications,
    withdraw_application,
)


router = APIRouter(tags=["applications"])


@router.post(
    "/api/jobs/{job_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sinh viên ứng tuyển tin tuyển dụng",
)
async def api_apply_to_job(
    job_id: int,
    cv: UploadFile = File(..., description="CV PDF hoặc DOCX, tối đa 5 MB"),
    cover_letter: str | None = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    content = await cv.read(MAX_CV_SIZE + 1)
    return apply_to_job(
        db,
        current_user,
        job_id,
        cv.filename,
        cv.content_type,
        content,
        cover_letter,
    )


@router.get(
    "/api/applications/my",
    response_model=list[MyApplicationResponse],
    summary="Danh sách đơn ứng tuyển của sinh viên hiện tại",
)
def api_get_my_applications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    return get_my_applications(db, current_user)


@router.post(
    "/api/applications/{application_id}/withdraw",
    response_model=MyApplicationResponse,
    summary="Sinh viên rút đơn đang chờ",
)
def api_withdraw_application(
    application_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    application = withdraw_application(db, current_user, application_id)
    return {
        "id": application.id,
        "job_id": application.job_id,
        "job_title": application.job.title,
        "status": application.status,
        "applied_at": application.applied_at,
        "cover_letter": application.cover_letter,
    }
