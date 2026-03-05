"""Tests for Toss (비바리퍼블리카) career crawler."""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.toss import TossCareerCrawler


TOSS_JOB_LIST_RESPONSE = {
    "resultType": "SUCCESS",
    "success": [
        {
            "id": 5793632003,
            "title": "Backend Engineer (Core Banking)",
            "absolute_url": "https://toss.im/career/jobs/5793632003",
            "location": {"name": "Seoul, Korea"},
            "updated_at": "2026-02-20T12:00:00.000Z",
            "first_published": "2026-01-10T09:00:00.000Z",
            "company_name": "Toss",
            "metadata": [],
        },
        {
            "id": 5793632004,
            "title": "Frontend Engineer (React)",
            "absolute_url": "https://toss.im/career/jobs/5793632004",
            "location": {"name": "Seoul, Korea"},
            "updated_at": "2026-02-25T12:00:00.000Z",
            "first_published": "2026-01-15T09:00:00.000Z",
            "company_name": "Toss",
            "metadata": [],
        },
    ],
}

GREENHOUSE_DETAIL_5793632003 = {
    "id": 5793632003,
    "title": "Backend Engineer (Core Banking)",
    "content": (
        "<p>We are looking for a Backend Engineer.</p>"
        "<h3>담당업무</h3>"
        "<ul><li>Core banking 시스템 개발</li><li>API 설계 및 구현</li></ul>"
        "<h3>자격요건</h3>"
        "<ul><li>Java, Spring Boot 3년 이상</li><li>RDB 경험</li></ul>"
        "<h3>우대사항</h3>"
        "<ul><li>Kafka 경험</li><li>대용량 트래픽 처리 경험</li></ul>"
        "<h3>복리후생</h3>"
        "<ul><li>스톡옵션</li><li>유연근무</li></ul>"
    ),
    "absolute_url": "https://toss.im/career/jobs/5793632003",
    "location": {"name": "Seoul, Korea"},
    "updated_at": "2026-02-20T12:00:00.000Z",
}

GREENHOUSE_DETAIL_5793632004 = {
    "id": 5793632004,
    "title": "Frontend Engineer (React)",
    "content": (
        "<p>We are looking for a Frontend Engineer.</p>"
        "<h3>자격요건</h3>"
        "<ul><li>React, TypeScript 경험</li></ul>"
    ),
    "absolute_url": "https://toss.im/career/jobs/5793632004",
    "location": {"name": "Seoul, Korea"},
    "updated_at": "2026-02-25T12:00:00.000Z",
}


class TestTossCrawlerInit:

    def test_source_name(self) -> None:
        crawler = TossCareerCrawler()
        assert crawler.get_source_name() == "toss_career"

    def test_rate_limit(self) -> None:
        crawler = TossCareerCrawler()
        assert crawler.get_rate_limit_delay() == 1.0


class TestTossJobList:

    @responses.activate
    def test_fetch_job_list_success(self) -> None:
        responses.add(
            responses.GET,
            "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs",
            json=TOSS_JOB_LIST_RESPONSE,
            status=200,
        )

        crawler = TossCareerCrawler()
        jobs = crawler._fetch_job_list()

        assert len(jobs) == 2
        assert jobs[0]["id"] == 5793632003
        assert jobs[0]["title"] == "Backend Engineer (Core Banking)"

    @responses.activate
    def test_fetch_job_list_api_error_returns_empty(self) -> None:
        responses.add(
            responses.GET,
            "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs",
            status=500,
        )

        crawler = TossCareerCrawler()
        jobs = crawler._fetch_job_list()
        assert jobs == []

    @responses.activate
    def test_fetch_job_list_empty_success(self) -> None:
        responses.add(
            responses.GET,
            "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs",
            json={"resultType": "SUCCESS", "success": []},
            status=200,
        )

        crawler = TossCareerCrawler()
        jobs = crawler._fetch_job_list()
        assert jobs == []


class TestTossGreenhouseDetail:

    @responses.activate
    def test_fetch_greenhouse_detail_success(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=GREENHOUSE_DETAIL_5793632003,
            status=200,
        )

        crawler = TossCareerCrawler()
        detail = crawler._fetch_greenhouse_detail(5793632003)

        assert detail is not None
        assert detail["title"] == "Backend Engineer (Core Banking)"
        assert "content" in detail

    @responses.activate
    def test_fetch_greenhouse_detail_404_returns_none(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/9999",
            status=404,
        )

        crawler = TossCareerCrawler()
        detail = crawler._fetch_greenhouse_detail(9999)
        assert detail is None


class TestTossJobToPosting:

    @responses.activate
    def test_job_to_posting_basic_fields(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=GREENHOUSE_DETAIL_5793632003,
            status=200,
        )

        crawler = TossCareerCrawler()
        job = TOSS_JOB_LIST_RESPONSE["success"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.title == "Backend Engineer (Core Banking)"
        assert posting.company_name == "비바리퍼블리카"
        assert posting.source_platform == "toss_career"
        assert posting.source_url == "https://toss.im/career/jobs/5793632003"
        assert posting.location == "Seoul, Korea"

    @responses.activate
    def test_job_to_posting_strips_html(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=GREENHOUSE_DETAIL_5793632003,
            status=200,
        )

        crawler = TossCareerCrawler()
        job = TOSS_JOB_LIST_RESPONSE["success"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "<p>" not in posting.description_raw
        assert "<ul>" not in posting.description_raw
        assert "Java" in posting.description_raw

    @responses.activate
    def test_job_to_posting_sections_extracted(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=GREENHOUSE_DETAIL_5793632003,
            status=200,
        )

        crawler = TossCareerCrawler()
        job = TOSS_JOB_LIST_RESPONSE["success"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.requirements_raw is not None
        assert "Java" in posting.requirements_raw
        assert posting.preferred_raw is not None
        assert "Kafka" in posting.preferred_raw
        assert posting.responsibilities_raw is not None
        assert posting.benefits_raw is not None

    @responses.activate
    def test_job_to_posting_masks_email(self) -> None:
        detail_with_email = {
            **GREENHOUSE_DETAIL_5793632003,
            "content": "<p>Contact hr@toss.im for questions.</p>",
        }
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=detail_with_email,
            status=200,
        )

        crawler = TossCareerCrawler()
        job = TOSS_JOB_LIST_RESPONSE["success"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "hr@toss.im" not in posting.description_raw
        assert "[EMAIL]" in posting.description_raw

    @responses.activate
    def test_job_to_posting_masks_phone(self) -> None:
        detail_with_phone = {
            **GREENHOUSE_DETAIL_5793632003,
            "content": "<p>문의: 02-1234-5678</p>",
        }
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=detail_with_phone,
            status=200,
        )

        crawler = TossCareerCrawler()
        job = TOSS_JOB_LIST_RESPONSE["success"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "02-1234-5678" not in posting.description_raw
        assert "[PHONE]" in posting.description_raw

    @responses.activate
    def test_job_to_posting_greenhouse_detail_fails_uses_title(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            status=404,
        )

        crawler = TossCareerCrawler()
        job = TOSS_JOB_LIST_RESPONSE["success"][0]
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.title == "Backend Engineer (Core Banking)"
        assert posting.description_raw == "Backend Engineer (Core Banking)"
        assert posting.requirements_raw is None

    def test_job_to_posting_missing_id_returns_none(self) -> None:
        crawler = TossCareerCrawler()
        posting = crawler._job_to_posting({"title": "No ID Job"})
        assert posting is None


class TestTossFullCrawl:

    @responses.activate
    def test_full_crawl_pipeline(self) -> None:
        responses.add(
            responses.GET,
            "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs",
            json=TOSS_JOB_LIST_RESPONSE,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632003",
            json=GREENHOUSE_DETAIL_5793632003,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/toss/jobs/5793632004",
            json=GREENHOUSE_DETAIL_5793632004,
            status=200,
        )

        crawler = TossCareerCrawler()
        postings = crawler.crawl()

        assert len(postings) == 2
        assert all(p.company_name == "비바리퍼블리카" for p in postings)
        assert all(p.source_platform == "toss_career" for p in postings)

    @responses.activate
    def test_full_crawl_empty_list(self) -> None:
        responses.add(
            responses.GET,
            "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs",
            json={"resultType": "SUCCESS", "success": []},
            status=200,
        )

        crawler = TossCareerCrawler()
        postings = crawler.crawl()
        assert postings == []
