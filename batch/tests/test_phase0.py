"""Tests for Phase 0 validation pipeline."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.skill_matcher import SkillMatcher
from phase0_validate import (
    analyze_by_category,
    analyze_by_company,
    analyze_skill_frequency,
    extract_skills_from_postings,
    generate_report,
    load_postings_from_csv,
)


@pytest.fixture
def seed_matcher() -> SkillMatcher:
    """SkillMatcher with full seed data."""
    seed_path = Path(__file__).parent.parent.parent / "data" / "skills_seed.json"
    return SkillMatcher(skills_path=seed_path)


@pytest.fixture
def sample_postings() -> list[dict]:
    return [
        {
            "title": "백엔드 개발자",
            "company": "네이버",
            "description": "Java, Spring Boot 기반 서버 개발. AWS 경험. MySQL, Redis 우대.",
        },
        {
            "title": "서버 개발자",
            "company": "쿠팡",
            "description": "Java/Kotlin 기반. Spring Boot, Docker. Kafka 경험 우대.",
        },
        {
            "title": "Backend Engineer",
            "company": "토스",
            "description": "Kotlin, Spring Boot. PostgreSQL. Kubernetes 운영 경험.",
        },
    ]


class TestLoadCSV:
    def test_load_sample_csv(self) -> None:
        csv_path = Path(__file__).parent.parent.parent / "data" / "sample_postings.csv"
        if not csv_path.exists():
            pytest.skip("sample_postings.csv not found")
        postings = load_postings_from_csv(csv_path)
        assert len(postings) == 20
        assert "title" in postings[0]
        assert "company" in postings[0]
        assert "description" in postings[0]


class TestExtractSkills:
    def test_extracts_known_skills(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        assert not df.empty
        skill_names = set(df["skill_name"].tolist())
        assert "Java" in skill_names
        assert "Spring Boot" in skill_names

    def test_trend_only_excluded(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        # Add a posting with trend-only keyword
        postings = sample_postings + [
            {
                "title": "개발자",
                "company": "테스트",
                "description": "vibe coding is the future. Java 필수.",
            }
        ]
        df = extract_skills_from_postings(postings, seed_matcher)
        skill_names = set(df["skill_name"].tolist())
        assert "vibe coding" not in skill_names  # TREND scope excluded
        assert "Java" in skill_names

    def test_has_required_columns(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        expected_cols = {"posting_idx", "title", "company", "skill_name", "category", "source_scope"}
        assert expected_cols.issubset(set(df.columns))


class TestAnalysis:
    def test_frequency_ranking(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        freq = analyze_skill_frequency(df, len(sample_postings))
        assert not freq.empty
        assert "rank" in freq.columns
        assert "percentage" in freq.columns
        assert freq.iloc[0]["rank"] == 1
        # Spring Boot should be in top 3 (all 3 postings mention it)
        top3 = set(freq.head(3)["skill_name"].tolist())
        assert "Spring Boot" in top3

    def test_frequency_percentage_calculation(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        freq = analyze_skill_frequency(df, len(sample_postings))
        # A skill in all 3 postings should be 100%
        all_present = freq[freq["count"] == 3]
        if not all_present.empty:
            assert all_present.iloc[0]["percentage"] == 100.0

    def test_company_analysis(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        company_df = analyze_by_company(df)
        assert not company_df.empty
        companies = set(company_df["company"].tolist())
        assert "네이버" in companies

    def test_category_analysis(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        cat_df = analyze_by_category(df, len(sample_postings))
        assert not cat_df.empty
        categories = set(cat_df["category"].tolist())
        assert "framework" in categories
        assert "language" in categories

    def test_empty_data(self) -> None:
        import pandas as pd

        empty_df = pd.DataFrame(columns=["posting_idx", "title", "company", "skill_name", "category"])
        freq = analyze_skill_frequency(empty_df, 0)
        assert freq.empty


class TestReport:
    def test_report_generation(
        self, sample_postings: list[dict], seed_matcher: SkillMatcher
    ) -> None:
        df = extract_skills_from_postings(sample_postings, seed_matcher)
        total = len(sample_postings)
        freq = analyze_skill_frequency(df, total)
        company_df = analyze_by_company(df)
        cat_df = analyze_by_category(df, total)
        report = generate_report(freq, company_df, cat_df, total)
        assert "DevPulse Phase 0" in report
        assert "3건" in report  # total_postings
        assert "Spring Boot" in report
