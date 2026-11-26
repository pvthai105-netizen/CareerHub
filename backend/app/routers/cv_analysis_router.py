from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app import deps
from app.models.user import Role, User
from app.schemas.cv_analysis import CVAnalysisResponse
from app.services.application_services import MAX_CV_SIZE
from app.services.cv_analysis_services import analyze_cv

router = APIRouter(
    prefix="/api/students/me/cv-analyses",
    tags=["CV analysis"],
)


@router.post(
    "",
    response_model=CVAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Phân tích CV PDF hoặc DOCX",
)
async def api_analyze_cv(
    file: UploadFile = File(..., description="CV PDF hoặc DOCX, tối đa 5 MB"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(Role.student)),
):
    content = await file.read(MAX_CV_SIZE + 1)
    return analyze_cv(db, current_user, file.filename, file.content_type, content)
