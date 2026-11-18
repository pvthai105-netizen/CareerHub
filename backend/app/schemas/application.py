from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.applications import ApplicationStatus


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    student_id: int
    status: ApplicationStatus
    applied_at: datetime
    cover_letter: str | None

    model_config = ConfigDict(from_attributes=True)


class MyApplicationResponse(BaseModel):
    id: int
    job_id: int
    job_title: str
    status: ApplicationStatus
    applied_at: datetime
    cover_letter: str | None

    model_config = ConfigDict(from_attributes=True)
