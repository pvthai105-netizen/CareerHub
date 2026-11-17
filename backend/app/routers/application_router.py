from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app import deps
from app.models.user import Role, User
from app.schemas.application import ApplicationResponse
from app.services.application_services import MAX_CV_SIZE, apply_to_job


router = APIRouter(prefix="/api/jobs", tags=["applications"])


@router.post(
    "/{job_id}/applications",
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
