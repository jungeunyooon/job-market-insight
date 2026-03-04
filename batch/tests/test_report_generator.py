"""Tests for automated report generator."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from report.generator import ReportGenerator, ReportData


@pytest.fixture
def sample_data() -> ReportData:
    return ReportData(
        generated_at="2026-03-04",
        skill_ranking=[
            {"rank": 1, "skill": "Java", "count": 465, "percentage": 88.9},
            {"rank": 2, "skill": "Spring Boot", "count": 429, "percentage": 82.0},
            {"rank": 3, "skill": "AWS", "count": 351, "percentage": 67.1},
        ],
        total_postings=523,
        company_profiles=[
            {
                "company": "카카오",
                "total_postings": 45,
                "top_skills": [
                    {"skill": "Kotlin", "count": 30},
                    {"skill": "Spring Boot", "count": 28},
                ],
            },
        ],
        position_comparison={
            "BACKEND": ["Java", "Spring Boot", "MySQL"],
            "PRODUCT": ["TypeScript", "React", "Node.js"],
            "common": ["Docker", "AWS"],
        },
        buzz_vs_hiring=[
            {"skill": "LangChain", "classification": "OVERHYPED",
             "trend_mentions": 47, "job_postings": 16},
            {"skill": "Kafka", "classification": "ADOPTED",
             "trend_mentions": 12, "job_postings": 251},
            {"skill": "Java", "classification": "ESTABLISHED",
             "trend_mentions": 5, "job_postings": 465},
        ],
        blog_topics={
            "yearly_trend": {
                2023: [{"skill": "Kafka", "count": 10}, {"skill": "Spring Boot", "count": 8}],
                2024: [{"skill": "Kafka", "count": 15}, {"skill": "Kotlin", "count": 12}],
            },
        },
    )


@pytest.fixture
def generator() -> ReportGenerator:
    return ReportGenerator()


class TestReportGeneration:

    def test_generates_markdown(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_has_title(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "# DevPulse" in report

    def test_has_date(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "2026-03-04" in report

    def test_has_skill_ranking_section(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "스킬 랭킹" in report
        assert "Java" in report
        assert "88.9" in report

    def test_has_company_profile_section(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "카카오" in report
        assert "Kotlin" in report

    def test_has_position_comparison_section(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "포지션" in report
        assert "BACKEND" in report
        assert "Docker" in report

    def test_has_buzz_vs_hiring_section(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "Buzz" in report or "buzz" in report.lower()
        assert "OVERHYPED" in report
        assert "ADOPTED" in report
        assert "LangChain" in report

    def test_has_blog_trend_section(self, generator: ReportGenerator, sample_data: ReportData) -> None:
        report = generator.generate(sample_data)
        assert "블로그" in report or "Blog" in report
        assert "2023" in report
        assert "2024" in report


class TestReportSave:

    def test_save_to_file(self, generator: ReportGenerator, sample_data: ReportData, tmp_path: Path) -> None:
        output = tmp_path / "report.md"
        generator.save(sample_data, output)
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "# DevPulse" in content

    def test_save_creates_parent_dirs(self, generator: ReportGenerator, sample_data: ReportData, tmp_path: Path) -> None:
        output = tmp_path / "reports" / "2026" / "report.md"
        generator.save(sample_data, output)
        assert output.exists()


class TestEmptyData:

    def test_empty_skill_ranking(self, generator: ReportGenerator) -> None:
        data = ReportData(generated_at="2026-03-04", skill_ranking=[], total_postings=0)
        report = generator.generate(data)
        assert "# DevPulse" in report
        assert "데이터 없음" in report or "0" in report

    def test_partial_data(self, generator: ReportGenerator) -> None:
        data = ReportData(
            generated_at="2026-03-04",
            skill_ranking=[{"rank": 1, "skill": "Java", "count": 10, "percentage": 100.0}],
            total_postings=10,
        )
        report = generator.generate(data)
        assert "Java" in report
