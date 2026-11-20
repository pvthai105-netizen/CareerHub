from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, require_roles
from app.models.user import Role, User
from app.schemas.ai_job_search import AIJobSearchRequest, AIJobSearchResponse
from app.services.ai_job_search_service import search_jobs_with_ai

router = APIRouter(prefix="/api/jobs", tags=["AI job search"])


@router.post("/ai-search", response_model=AIJobSearchResponse, summary="Tìm việc phù hợp bằng AI",)
def api_search_jobs_with_ai(payload: AIJobSearchRequest, db: Session = Depends(get_db), _current_user: User = Depends(require_roles(Role.student)),):
    return search_jobs_with_ai(db, payload.query)
