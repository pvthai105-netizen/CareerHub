from types import SimpleNamespace

from app.models.job import Job, JobType
from app.schemas.ai_job_search import AIJobSearchCriteria
from app.services import ai_job_search_service


def test_keyword_fallback_extracts_known_filters_and_skills():
    job = SimpleNamespace(
        industry="Công nghệ thông tin",
        location="Hà Nội",
    )

    criteria = ai_job_search_service._keyword_fallback(
        "Tìm thực tập ngành Công nghệ thông tin tại Hà Nội, lương 5-7 triệu, biết Python",
        [job],
    )

    assert criteria.industry == "Công nghệ thông tin"
    assert criteria.location == "Hà Nội"
    assert criteria.salary_min == 5_000_000
    assert criteria.salary_max == 7_000_000
    assert criteria.job_type == JobType.INTERNSHIP
    assert criteria.skills == ["Python"]


def test_keyword_fallback_does_not_treat_experience_as_salary():
    salary_min, salary_max = ai_job_search_service._extract_salary(
        "Tìm việc yêu cầu 3-5 năm kinh nghiệm với Python"
    )

    assert salary_min is None
    assert salary_max is None


def test_score_uses_equal_weights_and_partial_skill_match():
    job = SimpleNamespace(
        industry="Công nghệ thông tin",
        location="Hà Nội",
        salary_min=5_000_000,
        salary_max=8_000_000,
        job_type="INTERNSHIP",
        title="Thực tập sinh Python",
        description="Phát triển API bằng Python.",
    )
    criteria = AIJobSearchCriteria(
        industry="Công nghệ thông tin",
        location="Ha Noi",
        salary_min=6_000_000,
        job_type=JobType.INTERNSHIP,
        skills=["Python", "Java"],
    )

    score, reasons = ai_job_search_service._score_job(job, criteria)

    assert score == 90
    assert len(reasons) == 5
    assert "Kỹ năng khớp: Python; chưa thấy: Java" in reasons


def test_search_returns_only_top_ten_ranked_results(monkeypatch):
    jobs = [
        SimpleNamespace(
            job_id=job_id,
            industry="Công nghệ thông tin",
            location="Hà Nội" if job_id == 12 else "Đà Nẵng",
            salary_min=5_000_000,
            salary_max=8_000_000,
            job_type="INTERNSHIP",
            title="Python Intern",
            description="Python",
        )
        for job_id in range(1, 13)
    ]

    class FakeQuery:
        def filter(self, *_conditions):
            return self

        def all(self):
            return jobs

    class FakeSession:
        def query(self, model):
            assert model is Job
            return FakeQuery()

    monkeypatch.setattr(
        ai_job_search_service,
        "_extract_criteria",
        lambda _query, _available_jobs: (
            AIJobSearchCriteria(location="Hà Nội"),
            False,
        ),
    )

    result = ai_job_search_service.search_jobs_with_ai(FakeSession(), "Python intern")

    assert len(result["items"]) == 10
    assert result["items"][0]["job"].job_id == 12
    assert result["items"][0]["match_percentage"] == 100
    assert "tỷ lệ kỹ năng khớp" in result["score_formula"]
