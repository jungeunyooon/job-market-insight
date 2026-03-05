"""Tests for Greenhouse Board API crawler."""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.greenhouse import GreenhouseCrawler


SAMPLE_JOB_LIST = {
    "jobs": [
        {
            "id": 1001,
            "title": "Backend Engineer",
            "absolute_url": "https://boards.greenhouse.io/coupang/jobs/1001",
            "location": {"name": "Seoul, South Korea"},
            "updated_at": "2026-02-28T09:00:00-05:00",
            "metadata": [
                {"name": "Department", "value": "Engineering"},
            ],
        },
        {
            "id": 1002,
            "title": "Senior Software Engineer - Java",
            "absolute_url": "https://boards.greenhouse.io/coupang/jobs/1002",
            "location": {"name": "Seoul, South Korea"},
            "updated_at": "2026-03-01T10:00:00-05:00",
            "metadata": [],
        },
    ]
}

SAMPLE_JOB_DETAIL = {
    "id": 1001,
    "title": "Backend Engineer",
    "content": "<p>We are looking for a Backend Engineer.</p>"
               "<h3>Requirements</h3>"
               "<ul><li>Java, Spring Boot experience</li>"
               "<li>Kafka, Redis experience</li></ul>"
               "<h3>Preferred</h3>"
               "<ul><li>Kubernetes experience</li></ul>",
    "absolute_url": "https://boards.greenhouse.io/coupang/jobs/1001",
    "location": {"name": "Seoul, South Korea"},
    "departments": [{"name": "Engineering"}],
    "updated_at": "2026-02-28T09:00:00-05:00",
}


class TestGreenhouseCrawlerInit:

    def test_source_name(self) -> None:
        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        assert crawler.get_source_name() == "greenhouse"

    def test_default_rate_limit(self) -> None:
        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        assert crawler.get_rate_limit_delay() == 1.0

    def test_custom_board_tokens(self) -> None:
        tokens = {"쿠팡": "coupang", "두나무": "dunamu"}
        crawler = GreenhouseCrawler(board_tokens=tokens)
        assert len(crawler._board_tokens) == 2


class TestGreenhouseJobList:

    @responses.activate
    def test_fetch_job_list(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs",
            json=SAMPLE_JOB_LIST,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        jobs = crawler._fetch_job_list("coupang")

        assert len(jobs) == 2
        assert jobs[0]["id"] == 1001
        assert jobs[0]["title"] == "Backend Engineer"

    @responses.activate
    def test_empty_board(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/dunamu/jobs",
            json={"jobs": []},
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"dunamu": "dunamu"})
        jobs = crawler._fetch_job_list("dunamu")
        assert jobs == []

    @responses.activate
    def test_api_error_returns_empty(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs",
            status=500,
        )

        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        jobs = crawler._fetch_job_list("coupang")
        assert jobs == []


class TestGreenhouseJobDetail:

    @responses.activate
    def test_fetch_job_detail(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/1001",
            json=SAMPLE_JOB_DETAIL,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        detail = crawler._fetch_job_detail("coupang", 1001)

        assert detail is not None
        assert detail["title"] == "Backend Engineer"
        assert "content" in detail

    @responses.activate
    def test_detail_converts_to_posting(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/1001",
            json=SAMPLE_JOB_DETAIL,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        posting = crawler._detail_to_posting("coupang", "쿠팡", SAMPLE_JOB_LIST["jobs"][0])

        assert posting is not None
        assert posting.title == "Backend Engineer"
        assert posting.company_name == "쿠팡"
        assert posting.source_platform == "greenhouse"
        assert "boards.greenhouse.io" in posting.source_url

    @responses.activate
    def test_detail_strips_html(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/1001",
            json=SAMPLE_JOB_DETAIL,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        posting = crawler._detail_to_posting("coupang", "쿠팡", SAMPLE_JOB_LIST["jobs"][0])

        assert posting is not None
        assert "<p>" not in posting.description_raw
        assert "<ul>" not in posting.description_raw
        assert "Java" in posting.description_raw

    @responses.activate
    def test_handles_missing_detail(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/9999",
            status=404,
        )

        crawler = GreenhouseCrawler(board_tokens={"coupang": "coupang"})
        job_stub = {"id": 9999, "title": "Deleted", "absolute_url": "http://x", "location": {"name": ""}}
        posting = crawler._detail_to_posting("coupang", "쿠팡", job_stub)
        assert posting is None


class TestGreenhouseFullCrawl:

    @responses.activate
    def test_full_crawl_pipeline(self) -> None:
        # List endpoint
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs",
            json=SAMPLE_JOB_LIST,
            status=200,
        )
        # Detail for job 1001
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/1001",
            json=SAMPLE_JOB_DETAIL,
            status=200,
        )
        # Detail for job 1002
        detail_1002 = {**SAMPLE_JOB_DETAIL, "id": 1002, "title": "Senior Software Engineer - Java"}
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/1002",
            json=detail_1002,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"쿠팡": "coupang"})
        postings = crawler.crawl()

        assert len(postings) == 2
        assert all(p.company_name == "쿠팡" for p in postings)
        assert all(p.source_platform == "greenhouse" for p in postings)

    @responses.activate
    def test_multi_board_crawl(self) -> None:
        # Coupang board
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs",
            json={"jobs": [SAMPLE_JOB_LIST["jobs"][0]]},
            status=200,
        )
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/coupang/jobs/1001",
            json=SAMPLE_JOB_DETAIL,
            status=200,
        )
        # Dunamu board
        dunamu_job = {**SAMPLE_JOB_LIST["jobs"][1], "id": 2001,
                      "absolute_url": "https://boards.greenhouse.io/dunamu/jobs/2001"}
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/dunamu/jobs",
            json={"jobs": [dunamu_job]},
            status=200,
        )
        dunamu_detail = {**SAMPLE_JOB_DETAIL, "id": 2001, "title": "Senior Software Engineer - Java"}
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/dunamu/jobs/2001",
            json=dunamu_detail,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"쿠팡": "coupang", "두나무": "dunamu"})
        postings = crawler.crawl()

        assert len(postings) == 2
        companies = {p.company_name for p in postings}
        assert "쿠팡" in companies
        assert "두나무" in companies


DAANGN_JOB_LIST = {
    "jobs": [
        {
            "id": 3001,
            "title": "Backend Engineer (Kotlin)",
            "absolute_url": "https://boards.greenhouse.io/daangn/jobs/3001",
            "location": {"name": "Seoul, South Korea"},
            "updated_at": "2026-03-01T10:00:00-05:00",
            "metadata": [],
        },
    ]
}

DAANGN_JOB_DETAIL = {
    "id": 3001,
    "title": "Backend Engineer (Kotlin)",
    "content": "<p>당근마켓에서 백엔드 엔지니어를 찾습니다.</p>"
               "<h3>자격요건</h3>"
               "<ul><li>Kotlin, Spring Boot 경험</li>"
               "<li>MSA 설계 및 운영 경험</li></ul>"
               "<h3>우대사항</h3>"
               "<ul><li>Kubernetes 경험</li></ul>",
    "absolute_url": "https://boards.greenhouse.io/daangn/jobs/3001",
    "location": {"name": "Seoul, South Korea"},
    "departments": [{"name": "Engineering"}],
    "updated_at": "2026-03-01T10:00:00-05:00",
}


class TestGreenhouseDaangn:

    @responses.activate
    def test_daangn_job_list_fetch(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/daangn/jobs",
            json=DAANGN_JOB_LIST,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"당근마켓": "daangn"})
        jobs = crawler._fetch_job_list("daangn")

        assert len(jobs) == 1
        assert jobs[0]["id"] == 3001
        assert jobs[0]["title"] == "Backend Engineer (Kotlin)"

    @responses.activate
    def test_daangn_job_detail_fetch(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/daangn/jobs/3001",
            json=DAANGN_JOB_DETAIL,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"당근마켓": "daangn"})
        detail = crawler._fetch_job_detail("daangn", 3001)

        assert detail is not None
        assert detail["id"] == 3001
        assert detail["title"] == "Backend Engineer (Kotlin)"
        assert "content" in detail

    @responses.activate
    def test_daangn_posting_company_name(self) -> None:
        responses.add(
            responses.GET,
            "https://boards-api.greenhouse.io/v1/boards/daangn/jobs/3001",
            json=DAANGN_JOB_DETAIL,
            status=200,
        )

        crawler = GreenhouseCrawler(board_tokens={"당근마켓": "daangn"})
        posting = crawler._detail_to_posting("daangn", "당근마켓", DAANGN_JOB_LIST["jobs"][0])

        assert posting is not None
        assert posting.company_name == "당근마켓"
        assert posting.source_platform == "greenhouse"
        assert posting.title == "Backend Engineer (Kotlin)"
        assert "boards.greenhouse.io" in posting.source_url
