from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CVAnalysisResult(BaseModel):
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    missing_skills: list[str]
    score: int = Field(ge=0, le=100)
    improvement_suggestions: list[str]

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CVAnalysisResponse(CVAnalysisResult):
    id: int
    filename: str
    created_at: datetime
