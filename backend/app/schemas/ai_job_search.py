from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.job import JobType
from app.schemas.job import JobBaseSchema


class AIJobSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)

    model_config = ConfigDict(str_strip_whitespace=True)


class AIJobSearchCriteria(BaseModel):
    industry: str | None = None
    location: str | None = None
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    job_type: JobType | None = None
    skills: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("industry", "location", mode="before")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Tiêu chí văn bản phải là chuỗi.")
        cleaned = value.strip()
        return cleaned or None

    @field_validator("skills", mode="before")
    @classmethod
    def clean_skills(cls, value: list[str] | None) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Kỹ năng phải là danh sách.")
        if any(not isinstance(item, str) for item in value):
            raise ValueError("Mỗi kỹ năng phải là chuỗi.")
        return list(dict.fromkeys(item.strip() for item in value if item.strip()))

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("Lương tối thiểu không được lớn hơn lương tối đa.")
        return self


class AIJobRecommendation(BaseModel):
    job: JobBaseSchema
    match_percentage: int = Field(ge=0, le=100)
    reasons: list[str]


class AIJobSearchResponse(BaseModel):
    criteria: AIJobSearchCriteria
    used_fallback: bool
    score_formula: str
    items: list[AIJobRecommendation]
