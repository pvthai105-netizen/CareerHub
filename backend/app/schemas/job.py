from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.job import JobStatus, JobType


# ------------------ Request ------------------
class JobCreateSchema(BaseModel):
    title: str = Field(..., max_length=255, min_length=1)
    description: str = Field(..., min_length=1)
    industry: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    job_type: JobType
    deadline: date


class JobUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=255, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    industry: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = Field(None, min_length=1)
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    job_type: Optional[JobType]
    deadline: Optional[date]


class JobStatusPatchSchema(BaseModel):
    status: JobStatus


# ------------------ Response ------------------
class JobBaseSchema(BaseModel):
    job_id: int
    title: str
    description: str
    industry: str
    location: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    job_type: JobType
    deadline: date
    status: JobStatus
    employer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    total: int
    items: list[JobBaseSchema]