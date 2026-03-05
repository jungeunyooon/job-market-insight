"""Tests for Woowa Brothers (배달의민족) career crawler.

TDD: These tests define the expected behavior of WoowaCareerCrawler.
Uses responses library to mock HTTP requests — never hits real API.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.woowa import WoowaCareerCrawler

# ---------------------------------------------------------------------------
# Sample data — realistic shapes from career.woowahan.com/w1/recruits
# ---------------------------------------------------------------------------

JOB_1 = {
    "recruitSeq": 24028,
    "recruitNumber": "R2603009",
    "recruitName": "백엔드 개발자 (Java/Kotlin)",
    "recruitContents": (
        "우아한형제들 백엔드 개발자를 모십니다.\n"
        "담당업무\n"
        "- 배민 주문 서비스 백엔드 개발 및 운영\n"
        "- MSA 기반 서비스 설계\n"
        "자격요건\n"
        "- Java 또는 Kotlin 기반 서버 개발 경험 3년 이상\n"
        "- Spring Boot, JPA 실무 경험\n"
        "우대사항\n"
        "- Kafka, Redis 운영 경험\n"
        "- Kubernetes 기반 배포 경험\n"
        "복리후생\n"
        "- 유연 근무제, 재택근무\n"
    ),
    "recruitCorporationNumber": "WOOWA_BROTHERS",
    "recruitOpenDate": "2026-03-05 17:48:37",
    "recruitEndDate": "9999-12-31 00:00:00",
    "careerRestrictionMinYears": 3,
    "careerRestrictionMaxYears": 10,
    "keywords": [{"keyword": "Java"}, {"keyword": "Kotlin"}, {"keyword": "Spring Boot"}],
    "jobGroup": "개발",
    "employmentType": "정규직",
}

JOB_2 = {
    "recruitSeq": 24029,
    "recruitNumber": "R2603010",
    "recruitName": "데이터 엔지니어",
    "recruitContents": (
        "데이터 파이프라인을 구축하는 엔지니어를 모집합니다.\n"
        "담당업무\n"
        "- 실시간 데이터 파이프라인 개발\n"
        "자격요건\n"
        "- Python, Spark 경험 2년 이상\n"
        "우대사항\n"
        "- Airflow, Kafka 경험\n"
    ),
    "recruitSeq": 24029,
    "recruitNumber": "R2603010",
    "recruitName": "데이터 엔지니어",
    "recruitCorporationNumber": "WOOWA_BROTHERS",
    "recruitOpenDate": "2026-03-04 10:00:00",
    "recruitEndDate": "9999-12-31 00:00:00",
    "careerRestrictionMinYears": 2,
    "careerRestrictionMaxYears": 999,
    "keywords": [{"keyword": "Python"}, {"keyword": "Spark"}],
    "jobGroup": "데이터",
    "employmentType": "정규직",
}

JOB_3 = {
    "recruitSeq": 24030,
    "recruitNumber": "R2603011",
    "recruitName": "신입 iOS 개발자",
    "recruitContents": "iOS 앱 개발자를 모집합니다.",
    "recruitCorporationNumber": "WOOWA_BROTHERS",
    "recruitOpenDate": "2026-03-01 09:00:00",
    "recruitEndDate": "9999-12-31 00:00:00",
    "careerRestrictionMinYears": 0,
    "careerRestrictionMaxYears": 0,
    "keywords": [],
    "jobGroup": "개발",
    "employmentType": "정규직",
}

# Page 1: 2 jobs
PAGE_1_RESPONSE = {
    "code": "2000",
    "message": "OK",
    "data": {
        "pageSize": 25,
        "pageNumber": 1,
        "totalPageNumber": 2,
        "totalSize": 3,
        "list": [JOB_1, JOB_2],
    },
}

# Page 2: 1 job
PAGE_2_RESPONSE = {
    "code": "2000",
    "message": "OK",
    "data": {
        "pageSize": 25,
        "pageNumber": 2,
        "totalPageNumber": 2,
        "totalSize": 3,
        "list": [JOB_3],
    },
}

# Empty page (safety guard)
EMPTY_PAGE_RESPONSE = {
    "code": "2000",
    "message": "OK",
    "data": {
        "pageSize": 25,
        "pageNumber": 1,
        "totalPageNumber": 1,
        "totalSize": 0,
        "list": [],
    },
}

WOOWA_API_URL = "https://career.woowahan.com/w1/recruits"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def crawler() -> WoowaCareerCrawler:
    return WoowaCareerCrawler()


# ---------------------------------------------------------------------------
# Init / metadata tests
# ---------------------------------------------------------------------------


class TestWoowaCareerCrawlerInit:

    def test_source_name(self, crawler: WoowaCareerCrawler) -> None:
        assert crawler.get_source_name() == "woowa_career"

    def test_rate_limit_is_at_least_one_second(self, crawler: WoowaCareerCrawler) -> None:
        assert crawler.get_rate_limit_delay() >= 1.0


# ---------------------------------------------------------------------------
# Page fetching
# ---------------------------------------------------------------------------


class TestWoowaFetchPage:

    @responses.activate
    def test_fetch_page_returns_data(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(
            responses.GET,
            WOOWA_API_URL,
            json=PAGE_1_RESPONSE,
            status=200,
        )

        data = crawler._fetch_page(1)
        assert data is not None
        assert data["pageNumber"] == 1
        assert data["totalPageNumber"] == 2
        assert len(data["list"]) == 2

    @responses.activate
    def test_fetch_page_api_error_returns_none(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(
            responses.GET,
            WOOWA_API_URL,
            status=500,
        )

        data = crawler._fetch_page(1)
        assert data is None

    @responses.activate
    def test_fetch_page_non_2000_code_returns_none(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(
            responses.GET,
            WOOWA_API_URL,
            json={"code": "4001", "message": "Not Found", "data": {}},
            status=200,
        )

        data = crawler._fetch_page(1)
        assert data is None

    @responses.activate
    def test_fetch_page_empty_list(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(
            responses.GET,
            WOOWA_API_URL,
            json=EMPTY_PAGE_RESPONSE,
            status=200,
        )

        data = crawler._fetch_page(1)
        assert data is not None
        assert data["list"] == []


# ---------------------------------------------------------------------------
# Job → RawJobPosting conversion
# ---------------------------------------------------------------------------


class TestWoowaJobToPosting:

    def test_basic_fields(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.title == "백엔드 개발자 (Java/Kotlin)"
        assert posting.company_name == "우아한형제들"
        assert posting.source_platform == "woowa_career"

    def test_source_url_uses_recruit_number(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert "R2603009" in posting.source_url
        assert "career.woowahan.com" in posting.source_url

    def test_posted_at_parsed_correctly(self, crawler: WoowaCareerCrawler) -> None:
        from datetime import datetime

        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.posted_at == datetime(2026, 3, 5, 17, 48, 37)

    def test_tags_extracted_from_keywords(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert "Java" in posting.tags
        assert "Kotlin" in posting.tags
        assert "Spring Boot" in posting.tags

    def test_employment_type_mapped(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.employment_type == "정규직"

    def test_experience_level_range(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.experience_level == "3~10년"

    def test_experience_level_open_ended(self, crawler: WoowaCareerCrawler) -> None:
        """careerRestrictionMaxYears=999 이상은 'N년 이상'으로 표시된다."""
        posting = crawler._job_to_posting(JOB_2)

        assert posting is not None
        assert "이상" in (posting.experience_level or "")

    def test_experience_level_new_grad(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_3)

        assert posting is not None
        assert posting.experience_level == "신입"

    def test_empty_keywords_gives_empty_tags(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_3)

        assert posting is not None
        assert posting.tags == []

    def test_missing_recruit_number_and_seq_returns_none(self, crawler: WoowaCareerCrawler) -> None:
        bad_job = {**JOB_1, "recruitNumber": "", "recruitSeq": None}
        posting = crawler._job_to_posting(bad_job)
        assert posting is None


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------


class TestWoowaSectionExtraction:

    def test_requirements_extracted(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.requirements_raw is not None
        assert "Spring Boot" in posting.requirements_raw

    def test_preferred_extracted(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.preferred_raw is not None
        assert "Kafka" in posting.preferred_raw

    def test_responsibilities_extracted(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.responsibilities_raw is not None
        assert "MSA" in posting.responsibilities_raw

    def test_benefits_extracted(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_1)

        assert posting is not None
        assert posting.benefits_raw is not None
        assert "재택" in posting.benefits_raw

    def test_no_sections_returns_all_none(self, crawler: WoowaCareerCrawler) -> None:
        posting = crawler._job_to_posting(JOB_3)

        assert posting is not None
        assert posting.requirements_raw is None
        assert posting.preferred_raw is None
        assert posting.responsibilities_raw is None


# ---------------------------------------------------------------------------
# PII masking
# ---------------------------------------------------------------------------


class TestWoowaPIIMasking:

    def test_email_masked(self, crawler: WoowaCareerCrawler) -> None:
        job = {**JOB_3, "recruitContents": "문의: recruit@woowahan.com 로 연락 주세요."}
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "recruit@woowahan.com" not in posting.description_raw
        assert "[EMAIL]" in posting.description_raw

    def test_phone_masked(self, crawler: WoowaCareerCrawler) -> None:
        job = {**JOB_3, "recruitContents": "전화: 02-1234-5678 로 연락 주세요."}
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "02-1234-5678" not in posting.description_raw
        assert "[PHONE]" in posting.description_raw


# ---------------------------------------------------------------------------
# HTML content handling
# ---------------------------------------------------------------------------


class TestWoowaHTMLContent:

    def test_html_stripped_from_contents(self, crawler: WoowaCareerCrawler) -> None:
        job = {
            **JOB_3,
            "recruitContents": (
                "<p>백엔드 개발자를 모십니다.</p>"
                "<h3>자격요건</h3><ul><li>Java 경험</li></ul>"
            ),
        }
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "<p>" not in posting.description_raw
        assert "<ul>" not in posting.description_raw
        assert "Java" in posting.description_raw

    def test_html_sections_still_extracted(self, crawler: WoowaCareerCrawler) -> None:
        job = {
            **JOB_3,
            "recruitContents": (
                "<p>소개</p>"
                "<h3>자격요건</h3><ul><li>Kotlin 3년 이상</li></ul>"
                "<h3>우대사항</h3><ul><li>Docker 경험</li></ul>"
            ),
        }
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.requirements_raw is not None
        assert "Kotlin" in posting.requirements_raw
        assert posting.preferred_raw is not None
        assert "Docker" in posting.preferred_raw


# ---------------------------------------------------------------------------
# Full crawl with pagination
# ---------------------------------------------------------------------------


class TestWoowaFullCrawl:

    @responses.activate
    def test_full_crawl_two_pages(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(
            responses.GET,
            WOOWA_API_URL,
            json=PAGE_1_RESPONSE,
            status=200,
        )
        responses.add(
            responses.GET,
            WOOWA_API_URL,
            json=PAGE_2_RESPONSE,
            status=200,
        )

        postings = crawler.crawl()

        assert len(postings) == 3
        assert all(p.company_name == "우아한형제들" for p in postings)
        assert all(p.source_platform == "woowa_career" for p in postings)

    @responses.activate
    def test_full_crawl_titles_correct(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(responses.GET, WOOWA_API_URL, json=PAGE_1_RESPONSE, status=200)
        responses.add(responses.GET, WOOWA_API_URL, json=PAGE_2_RESPONSE, status=200)

        postings = crawler.crawl()
        titles = {p.title for p in postings}

        assert "백엔드 개발자 (Java/Kotlin)" in titles
        assert "데이터 엔지니어" in titles
        assert "신입 iOS 개발자" in titles

    @responses.activate
    def test_single_page_crawl(self, crawler: WoowaCareerCrawler) -> None:
        single_page = {
            "code": "2000",
            "message": "OK",
            "data": {
                "pageSize": 25,
                "pageNumber": 1,
                "totalPageNumber": 1,
                "totalSize": 1,
                "list": [JOB_1],
            },
        }
        responses.add(responses.GET, WOOWA_API_URL, json=single_page, status=200)

        postings = crawler.crawl()

        assert len(postings) == 1
        assert postings[0].title == "백엔드 개발자 (Java/Kotlin)"

    @responses.activate
    def test_empty_crawl_returns_empty_list(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(responses.GET, WOOWA_API_URL, json=EMPTY_PAGE_RESPONSE, status=200)

        postings = crawler.crawl()
        assert postings == []

    @responses.activate
    def test_first_page_api_error_returns_empty(self, crawler: WoowaCareerCrawler) -> None:
        responses.add(responses.GET, WOOWA_API_URL, status=503)

        postings = crawler.crawl()
        assert postings == []
