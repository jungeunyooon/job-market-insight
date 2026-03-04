"""Tests for Jumpit crawler."""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.jumpit import JumpitCrawler

MOCK_JOB_LIST_RESPONSE = {
    "result": {
        "positions": [
            {"id": 5001, "title": "백엔드 개발자", "companyName": "토스"},
            {"id": 5002, "title": "서버 엔지니어", "companyName": "당근"},
        ]
    }
}

MOCK_JOB_LIST_EMPTY = {
    "result": {"positions": []}
}

MOCK_JOB_DETAIL_5001 = {
    "result": {
        "id": 5001,
        "title": "백엔드 개발자",
        "company": {"name": "토스"},
        "qualifications": "Java/Kotlin 기반 백엔드 개발 경험 3년 이상",
        "preferredQualifications": "MSA 설계 및 운영 경험. Kafka 사용 경험.",
        "responsibility": "핀테크 서비스 백엔드 API 개발 및 운영",
        "techStacks": [
            {"stack": "Kotlin"},
            {"stack": "Spring Boot"},
            {"stack": "Kafka"},
        ],
        "workingPlace": "서울 강남구",
    }
}

MOCK_JOB_DETAIL_5002 = {
    "result": {
        "id": 5002,
        "title": "서버 엔지니어",
        "company": {"name": "당근"},
        "qualifications": "Go 또는 Kotlin 기반 서버 개발 경험",
        "preferredQualifications": "대규모 분산 시스템 운영 경험",
        "responsibility": "로컬 커뮤니티 서비스 API 개발",
        "techStacks": [
            {"stack": "Go"},
            {"stack": "Kubernetes"},
            {"stack": "gRPC"},
        ],
        "workingPlace": "서울 서초구",
    }
}


@pytest.fixture
def crawler() -> JumpitCrawler:
    return JumpitCrawler(max_pages=1)


class TestJumpitCrawlerInit:
    def test_source_name(self, crawler: JumpitCrawler) -> None:
        assert crawler.get_source_name() == "jumpit"

    def test_rate_limit(self, crawler: JumpitCrawler) -> None:
        assert crawler.get_rate_limit_delay() >= 1.0


class TestJumpitCrawlerListJobs:
    @responses.activate
    def test_fetch_job_list(self, crawler: JumpitCrawler) -> None:
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/positions",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )

        jobs = crawler._fetch_job_list(page=1)
        assert len(jobs) == 2
        assert jobs[0]["id"] == 5001

    @responses.activate
    def test_empty_page(self, crawler: JumpitCrawler) -> None:
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/positions",
            json=MOCK_JOB_LIST_EMPTY,
            status=200,
        )

        jobs = crawler._fetch_job_list(page=1)
        assert len(jobs) == 0

    @responses.activate
    def test_handles_api_error(self, crawler: JumpitCrawler) -> None:
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/positions",
            status=500,
        )

        jobs = crawler._fetch_job_list(page=1)
        assert len(jobs) == 0


class TestJumpitCrawlerJobDetail:
    @responses.activate
    def test_fetch_job_detail(self, crawler: JumpitCrawler) -> None:
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/position/5001",
            json=MOCK_JOB_DETAIL_5001,
            status=200,
        )

        detail = crawler._fetch_job_detail(5001)
        assert detail is not None
        assert detail["result"]["title"] == "백엔드 개발자"

    @responses.activate
    def test_detail_builds_posting(self, crawler: JumpitCrawler) -> None:
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/position/5001",
            json=MOCK_JOB_DETAIL_5001,
            status=200,
        )

        posting = crawler._detail_to_posting(5001)
        assert posting is not None
        assert posting.company_name == "토스"
        assert posting.source_platform == "jumpit"
        assert "Kotlin" in posting.description_raw
        assert "Kafka" in posting.description_raw
        assert posting.tags == ["Kotlin", "Spring Boot", "Kafka"]

    @responses.activate
    def test_handles_not_found(self, crawler: JumpitCrawler) -> None:
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/position/99999",
            status=404,
        )

        detail = crawler._fetch_job_detail(99999)
        assert detail is None


class TestJumpitCrawlerFullCrawl:
    @responses.activate
    def test_full_crawl_pipeline(self, crawler: JumpitCrawler) -> None:
        # List page
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/positions",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        # Detail pages
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/position/5001",
            json=MOCK_JOB_DETAIL_5001,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.jumpit.co.kr/api/position/5002",
            json=MOCK_JOB_DETAIL_5002,
            status=200,
        )

        postings = crawler.crawl()
        assert len(postings) == 2
        assert postings[0].company_name == "토스"
        assert postings[1].company_name == "당근"
        assert all(p.source_platform == "jumpit" for p in postings)
