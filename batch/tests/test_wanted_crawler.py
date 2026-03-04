"""Tests for Wanted API crawler.

TDD: These tests define the expected behavior of WantedAPICrawler.
Uses responses library to mock HTTP requests — never hits real API.
"""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.wanted import WantedAPICrawler


# Mock API responses based on Wanted OpenAPI structure
MOCK_JOB_LIST_RESPONSE = {
    "data": [
        {
            "id": 12345,
            "position": "백엔드 개발자",
            "company": {
                "id": 100,
                "name": "네이버",
            },
            "location": "판교",
            "category": {"id": 518, "name": "서버 개발자"},
        },
        {
            "id": 12346,
            "position": "서버 엔지니어",
            "company": {
                "id": 200,
                "name": "쿠팡",
            },
            "location": "서울",
            "category": {"id": 518, "name": "서버 개발자"},
        },
    ],
    "links": {
        "next": "https://www.wanted.co.kr/api/v4/jobs?offset=20&limit=20",
    },
}

MOCK_JOB_LIST_LAST_PAGE = {
    "data": [],
    "links": {
        "next": None,
    },
}

MOCK_JOB_DETAIL_12345 = {
    "job": {
        "id": 12345,
        "position": "백엔드 개발자",
        "company": {
            "id": 100,
            "name": "네이버",
        },
        "location": "판교",
        "detail": {
            "requirements": "자격요건: Java, Spring Boot 기반 서버 개발 경험",
            "preferred": "우대사항: Kafka, Kubernetes 경험",
            "intro": "네이버 검색 서비스 백엔드 개발",
            "main_tasks": "검색 API 개발 및 운영",
        },
        "skill_tags": [
            {"id": 1, "title": "Java"},
            {"id": 2, "title": "Spring"},
        ],
        "due_time": "2026-04-01T00:00:00",
        "address": {
            "full_location": "경기도 성남시 분당구",
        },
    }
}

MOCK_JOB_DETAIL_12346 = {
    "job": {
        "id": 12346,
        "position": "서버 엔지니어",
        "company": {
            "id": 200,
            "name": "쿠팡",
        },
        "location": "서울",
        "detail": {
            "requirements": "Java/Kotlin 기반 백엔드 개발 경험. AWS 인프라 경험.",
            "preferred": "대용량 트래픽 처리 경험. Docker, Kubernetes.",
            "intro": "쿠팡 물류 플랫폼 서버 개발",
            "main_tasks": "물류 API 개발",
        },
        "skill_tags": [
            {"id": 1, "title": "Java"},
            {"id": 3, "title": "Kotlin"},
        ],
        "due_time": None,
        "address": {
            "full_location": "서울특별시 송파구",
        },
    }
}


@pytest.fixture
def crawler() -> WantedAPICrawler:
    return WantedAPICrawler(
        search_keywords=["백엔드", "서버 개발자"],
        max_pages=1,
    )


class TestWantedCrawlerInit:
    def test_source_name(self, crawler: WantedAPICrawler) -> None:
        assert crawler.get_source_name() == "wanted"

    def test_rate_limit(self, crawler: WantedAPICrawler) -> None:
        assert crawler.get_rate_limit_delay() >= 1.0


class TestWantedCrawlerListJobs:
    @responses.activate
    def test_fetch_job_list(self, crawler: WantedAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )

        jobs = crawler._fetch_job_list(keyword="백엔드", offset=0)
        assert len(jobs) == 2
        assert jobs[0]["id"] == 12345
        assert jobs[1]["id"] == 12346

    @responses.activate
    def test_empty_page_returns_empty(self, crawler: WantedAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_LAST_PAGE,
            status=200,
        )

        jobs = crawler._fetch_job_list(keyword="백엔드", offset=100)
        assert len(jobs) == 0

    @responses.activate
    def test_handles_api_error(self, crawler: WantedAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            status=500,
        )

        jobs = crawler._fetch_job_list(keyword="백엔드", offset=0)
        assert len(jobs) == 0


class TestWantedCrawlerJobDetail:
    @responses.activate
    def test_fetch_job_detail(self, crawler: WantedAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/12345",
            json=MOCK_JOB_DETAIL_12345,
            status=200,
        )

        detail = crawler._fetch_job_detail(12345)
        assert detail is not None
        assert detail["job"]["position"] == "백엔드 개발자"

    @responses.activate
    def test_detail_builds_description(self, crawler: WantedAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/12345",
            json=MOCK_JOB_DETAIL_12345,
            status=200,
        )

        posting = crawler._detail_to_posting(12345)
        assert posting is not None
        assert "Java" in posting.description_raw
        assert "Spring Boot" in posting.description_raw
        assert posting.source_platform == "wanted"
        assert posting.company_name == "네이버"

    @responses.activate
    def test_handles_missing_detail(self, crawler: WantedAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/99999",
            status=404,
        )

        detail = crawler._fetch_job_detail(99999)
        assert detail is None


class TestWantedCrawlerFullCrawl:
    @responses.activate
    def test_full_crawl_pipeline(self, crawler: WantedAPICrawler) -> None:
        # Mock list endpoint
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        # Second call returns empty (end of pages)
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_LAST_PAGE,
            status=200,
        )
        # Mock detail endpoints
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/12345",
            json=MOCK_JOB_DETAIL_12345,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/12346",
            json=MOCK_JOB_DETAIL_12346,
            status=200,
        )

        postings = crawler.crawl()
        assert len(postings) == 2
        assert postings[0].company_name == "네이버"
        assert postings[1].company_name == "쿠팡"
        assert all(p.source_platform == "wanted" for p in postings)

    @responses.activate
    def test_deduplicates_across_keywords(self) -> None:
        """Same job found by different keywords should not be duplicated."""
        crawler = WantedAPICrawler(
            search_keywords=["백엔드", "서버 개발자"],
            max_pages=1,
        )
        # Both keywords return the same job
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_LAST_PAGE,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs",
            json=MOCK_JOB_LIST_LAST_PAGE,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/12345",
            json=MOCK_JOB_DETAIL_12345,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.wanted.co.kr/api/v4/jobs/12346",
            json=MOCK_JOB_DETAIL_12346,
            status=200,
        )

        postings = crawler.crawl()
        # Should be 2, not 4 (dedup by job id)
        assert len(postings) == 2
