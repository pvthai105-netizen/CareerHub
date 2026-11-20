import logging
import re
import unicodedata
from datetime import date
from typing import Iterable

from fastapi import HTTPException, status
from google import genai
from google.genai import errors, types
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models.job import Job, JobStatus, JobType
from app.schemas.ai_job_search import AIJobSearchCriteria

logger = logging.getLogger(__name__)

SCORE_FORMULA = (
    "100 x (tổng điểm các tiêu chí / số tiêu chí được trích xuất); "
    "điểm kỹ năng là tỷ lệ kỹ năng khớp."
)
CRITERIA_SYSTEM_PROMPT = """
Trích xuất tiêu chí tìm việc từ yêu cầu tiếng Việt của sinh viên.
Chỉ trả về một JSON object có các khóa: industry, location, salary_min,
salary_max, job_type, skills. Dùng null khi không có tiêu chí; skills là
mảng chuỗi. salary_min và salary_max là số tiền VND. job_type chỉ nhận một
trong các giá trị FULL_TIME, PART_TIME, INTERNSHIP, REMOTE, CONTRACT.
Không suy diễn tiêu chí không được nêu và không trả lời giải thích ngoài JSON.
""".strip()

_JOB_TYPE_KEYWORDS = {
    JobType.INTERNSHIP: ("thuc tap", "intern", "internship"),
    JobType.PART_TIME: ("part time", "ban thoi gian", "ban thoi"),
    JobType.FULL_TIME: ("full time", "toan thoi gian"),
    JobType.REMOTE: ("remote", "tu xa", "tai nha"),
    JobType.CONTRACT: ("contract", "hop dong"),
}
_STOP_WORDS = {
    "ban", "biet", "can", "cho", "cong", "co", "gi", "hay", "la", "lam",
    "luong", "muon", "nganh", "o", "phu", "hop", "toi", "tim", "tuyen",
    "theo", "thuc", "tap", "tai", "viec", "voi", "va", "muc", "thu",
    "nhap", "ky", "nang", "tri", "trieu", "nghin", "ngan",
}
_MONEY_TOKEN = (
    r"(?P<{prefix}amount>\d+(?:[.,]\d+)?)\s*"
    r"(?P<{prefix}unit>trieu|tr|nghin|ngan|k|vnd|dong)?"
)


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    without_marks = "".join(
        character for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"\s+", " ", without_marks.replace("đ", "d")).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = _normalize_text(text)
    normalized_phrase = _normalize_text(phrase)
    return bool(
        normalized_phrase
        and re.search(
            rf"(?<![a-z0-9]){re.escape(normalized_phrase)}(?![a-z0-9])",
            normalized_text,
        )
    )


def _has_criteria(criteria: AIJobSearchCriteria) -> bool:
    return any(
        (
            criteria.industry,
            criteria.location,
            criteria.salary_min is not None,
            criteria.salary_max is not None,
            criteria.job_type,
            criteria.skills,
        )
    )


def _match_known_value(query: str, values: Iterable[str | None]) -> str | None:
    unique_values = {value.strip() for value in values if value and value.strip()}
    return next(
        (
            value
            for value in sorted(unique_values, key=len, reverse=True)
            if _contains_phrase(query, value)
        ),
        None,
    )


def _parse_money(amount: str, unit: str | None) -> float:
    value = float(amount.replace(",", "."))
    if unit in ("trieu", "tr"):
        return value * 1_000_000
    if unit in ("nghin", "ngan", "k"):
        return value * 1_000
    if unit in ("vnd", "dong"):
        return value
    return value * 1_000_000 if value < 10_000 else value


def _extract_salary(query: str) -> tuple[float | None, float | None]:
    normalized_query = _normalize_text(query)
    has_salary_context = re.search(
        r"\b(luong|thu nhap|salary|trieu|tr|nghin|ngan|vnd|dong)\b",
        normalized_query,
    ) or re.search(r"\d\s*(?:trieu|tr|nghin|ngan|k|vnd|dong)(?![a-z])", normalized_query)
    if not has_salary_context:
        return None, None

    range_pattern = (
        _MONEY_TOKEN.format(prefix="low_")
        + r"\s*(?:-|den|toi|to)\s*"
        + _MONEY_TOKEN.format(prefix="high_")
    )
    range_match = re.search(range_pattern, normalized_query)
    if range_match:
        shared_unit = range_match.group("low_unit") or range_match.group("high_unit")
        low = _parse_money(range_match.group("low_amount"), shared_unit)
        high = _parse_money(range_match.group("high_amount"), shared_unit)
        return min(low, high), max(low, high)

    single_match = re.search(_MONEY_TOKEN.format(prefix="single_"), normalized_query)
    if not single_match:
        return None, None
    amount = _parse_money(
        single_match.group("single_amount"),
        single_match.group("single_unit"),
    )
    if re.search(r"\b(duoi|toi da|khong qua)\b", normalized_query):
        return None, amount
    return amount, None


def _keyword_fallback(query: str, jobs: list[Job]) -> AIJobSearchCriteria:
    industry = _match_known_value(query, (job.industry for job in jobs))
    location = _match_known_value(query, (job.location for job in jobs))
    normalized_query = _normalize_text(query)
    job_type = next(
        (
            candidate
            for candidate, keywords in _JOB_TYPE_KEYWORDS.items()
            if any(_contains_phrase(normalized_query, keyword) for keyword in keywords)
        ),
        None,
    )
    salary_min, salary_max = _extract_salary(query)

    excluded_terms = {
        _normalize_text(term)
        for term in (
            industry or "",
            location or "",
            *(keyword for values in _JOB_TYPE_KEYWORDS.values() for keyword in values),
        )
        if term
    }
    excluded_terms.update(
        word
        for phrase in (industry or "", location or "")
        for word in _normalize_text(phrase).split()
    )
    excluded_terms.update(
        word
        for values in _JOB_TYPE_KEYWORDS.values()
        for keyword in values
        for word in _normalize_text(keyword).split()
    )
    skills: list[str] = []
    seen_skills: set[str] = set()
    for token in re.findall(r"[A-Za-zÀ-ỹ+#.]+", query, flags=re.IGNORECASE):
        normalized_token = _normalize_text(token).strip(".")
        if (
            len(normalized_token) < 2
            or normalized_token in _STOP_WORDS
            or normalized_token in seen_skills
            or normalized_token in excluded_terms
            or any(character.isdigit() for character in token)
        ):
            continue
        seen_skills.add(normalized_token)
        skills.append(token.strip("."))

    return AIJobSearchCriteria(
        industry=industry,
        location=location,
        salary_min=salary_min,
        salary_max=salary_max,
        job_type=job_type,
        skills=skills[:20],
    )


def _extract_criteria(query: str, jobs: list[Job]) -> tuple[AIJobSearchCriteria, bool]:
    if GEMINI_API_KEY:
        try:
            with genai.Client(api_key=GEMINI_API_KEY) as client:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=query,
                    config=types.GenerateContentConfig(
                        system_instruction=CRITERIA_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                    ),
                )
            if response.text:
                criteria = AIJobSearchCriteria.model_validate_json(response.text)
                if _has_criteria(criteria):
                    return criteria, False
            logger.warning("Gemini returned no usable job-search criteria; using keywords.")
        except (errors.APIError, ValidationError, TypeError) as exc:
            logger.warning(
                "Gemini job-search extraction failed; using keyword fallback (%s).",
                type(exc).__name__,
            )
    criteria = _keyword_fallback(query, jobs)
    if not _has_criteria(criteria):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Không trích xuất được tiêu chí tìm việc từ yêu cầu.",
        )
    return criteria, True


def _salary_matches(job: Job, criteria: AIJobSearchCriteria) -> bool:
    if job.salary_min is None and job.salary_max is None:
        return False
    job_min = float(job.salary_min) if job.salary_min is not None else float(job.salary_max)
    job_max = float(job.salary_max) if job.salary_max is not None else float(job.salary_min)
    wanted_min = criteria.salary_min if criteria.salary_min is not None else 0
    wanted_max = criteria.salary_max if criteria.salary_max is not None else float("inf")
    return job_max >= wanted_min and job_min <= wanted_max


def _score_job(job: Job, criteria: AIJobSearchCriteria) -> tuple[int, list[str]]:
    component_scores: list[float] = []
    reasons: list[str] = []

    if criteria.industry:
        matched = _contains_phrase(job.industry, criteria.industry)
        component_scores.append(float(matched))
        reasons.append(
            f"Ngành nghề {'khớp' if matched else 'chưa khớp'}: {criteria.industry}"
        )

    if criteria.location:
        matched = _contains_phrase(job.location, criteria.location)
        component_scores.append(float(matched))
        reasons.append(
            f"Địa điểm {'khớp' if matched else 'chưa khớp'}: {criteria.location}"
        )

    if criteria.salary_min is not None or criteria.salary_max is not None:
        matched = _salary_matches(job, criteria)
        component_scores.append(float(matched))
        reasons.append(
            "Mức lương phù hợp"
            if matched
            else "Mức lương không giao nhau với khoảng mong muốn hoặc tin chưa nêu lương"
        )

    if criteria.job_type is not None:
        matched = job.job_type == criteria.job_type.value
        component_scores.append(float(matched))
        reasons.append(
            f"Hình thức {'khớp' if matched else 'chưa khớp'}: {criteria.job_type.value}"
        )

    if criteria.skills:
        searchable_text = " ".join(
            (job.title or "", job.description or "", job.industry or "")
        )
        matched_skills = [
            skill for skill in criteria.skills
            if _contains_phrase(searchable_text, skill)
        ]
        component_scores.append(len(matched_skills) / len(criteria.skills))
        missing_skills = [skill for skill in criteria.skills if skill not in matched_skills]
        reason = f"Kỹ năng khớp: {', '.join(matched_skills)}" if matched_skills else "Chưa khớp kỹ năng nào"
        if missing_skills:
            reason += f"; chưa thấy: {', '.join(missing_skills)}"
        reasons.append(reason)

    percentage = round(sum(component_scores) / len(component_scores) * 100)
    return percentage, reasons


def search_jobs_with_ai(db: Session, query: str) -> dict:
    jobs = (
        db.query(Job)
        .filter(
            Job.status == JobStatus.ACTIVE.value,
            Job.deadline >= date.today(),
        )
        .all()
    )
    criteria, used_fallback = _extract_criteria(query, jobs)
    ranked_jobs = [
        (job, *_score_job(job, criteria))
        for job in jobs
    ]
    ranked_jobs.sort(key=lambda result: (-result[1], -(result[0].job_id or 0)))

    return {
        "criteria": criteria,
        "used_fallback": used_fallback,
        "score_formula": SCORE_FORMULA,
        "items": [
            {
                "job": job,
                "match_percentage": score,
                "reasons": reasons,
            }
            for job, score, reasons in ranked_jobs[:10]
        ],
    }
