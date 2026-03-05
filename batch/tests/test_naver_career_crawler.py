"""Tests for Naver Career crawler.

TDD: These tests define the expected behavior of NaverCareerCrawler.
Uses responses library to mock HTTP requests — never hits real API.
"""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.naver_career import NaverCareerCrawler


MOCK_JOB_LIST_RESPONSE = {
    "list": [
        {
            "annoId": "20240001",
            "annoSubject": "백엔드 개발자",
            "annoWorkPlace": "판교",
            "entTypeCd": "정규직",
            "jobType": "경력",
        },
        {
            "annoId": "20240002",
            "annoSubject": "서버 플랫폼 엔지니어",
            "annoWorkPlace": "서울",
            "entTypeCd": "정규직",
            "jobType": "경력무관",
        },
    ]
}

MOCK_JOB_LIST_EMPTY = {"list": []}

MOCK_DETAIL_HTML_20240001 = """
<html>
<body>
<div class="content_detail">
<h3>담당업무</h3>
<ul>
<li>검색 서비스 백엔드 API 개발</li>
<li>대규모 트래픽 처리 시스템 설계</li>
</ul>
<h3>자격요건</h3>
<ul>
<li>Java, Spring Boot 기반 서버 개발 경험 3년 이상</li>
<li>RDBMS 설계 및 운영 경험</li>
</ul>
<h3>우대사항</h3>
<ul>
<li>Kafka, Kubernetes 운영 경험</li>
<li>대규모 분산 시스템 경험</li>
</ul>
<h3>복리후생</h3>
<ul>
<li>자율 출퇴근</li>
<li>스톡옵션</li>
</ul>
</div>
</body>
</html>
"""

MOCK_DETAIL_HTML_20240002 = """
<html>
<body>
<div class="content_detail">
<h3>담당업무</h3>
<p>서버 플랫폼 인프라 운영 및 개발</p>
<h3>자격요건</h3>
<p>Python 또는 Go 개발 경험. Linux 시스템 이해.</p>
</div>
</body>
</html>
"""


@pytest.fixture
def crawler() -> NaverCareerCrawler:
    return NaverCareerCrawler(max_pages=1, page_size=10)


class TestNaverCareerInit:
    def test_source_name(self, crawler: NaverCareerCrawler) -> None:
        assert crawler.get_source_name() == "naver_career"

    def test_rate_limit(self, crawler: NaverCareerCrawler) -> None:
        assert crawler.get_rate_limit_delay() >= 1.0


class TestNaverCareerListJobs:
    @responses.activate
    def test_fetch_job_list(self, crawler: NaverCareerCrawler) -> None:
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )

        jobs = crawler._fetch_job_list(first_index=0)
        assert len(jobs) == 2
        assert jobs[0]["annoId"] == "20240001"

    @responses.activate
    def test_empty_list(self, crawler: NaverCareerCrawler) -> None:
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_EMPTY,
            status=200,
        )

        jobs = crawler._fetch_job_list(first_index=0)
        assert len(jobs) == 0

    @responses.activate
    def test_handles_api_error(self, crawler: NaverCareerCrawler) -> None:
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            status=500,
        )

        jobs = crawler._fetch_job_list(first_index=0)
        assert len(jobs) == 0


class TestNaverCareerDetail:
    @responses.activate
    def test_detail_extracts_structured_fields(self, crawler: NaverCareerCrawler) -> None:
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=MOCK_DETAIL_HTML_20240001,
            status=200,
        )

        item = {"annoId": "20240001", "annoSubject": "백엔드 개발자", "annoWorkPlace": "판교"}
        posting = crawler._detail_to_posting(item)

        assert posting is not None
        assert posting.title == "백엔드 개발자"
        assert posting.company_name == "네이버"
        assert posting.source_platform == "naver_career"
        assert "20240001" in posting.source_url

        # 구조화 필드 확인
        assert posting.requirements_raw is not None
        assert "Java" in posting.requirements_raw or "Spring Boot" in posting.requirements_raw
        assert posting.preferred_raw is not None
        assert "Kafka" in posting.preferred_raw or "Kubernetes" in posting.preferred_raw
        assert posting.responsibilities_raw is not None
        assert "검색" in posting.responsibilities_raw or "API" in posting.responsibilities_raw
        assert posting.benefits_raw is not None

    @responses.activate
    def test_detail_handles_missing_sections(self, crawler: NaverCareerCrawler) -> None:
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=MOCK_DETAIL_HTML_20240002,
            status=200,
        )

        item = {"annoId": "20240002", "annoSubject": "서버 플랫폼 엔지니어"}
        posting = crawler._detail_to_posting(item)

        assert posting is not None
        assert posting.requirements_raw is not None
        assert "Python" in posting.requirements_raw
        # 우대사항 없음 → None
        assert posting.preferred_raw is None
        # 복리후생 없음 → None
        assert posting.benefits_raw is None

    @responses.activate
    def test_pii_masking(self, crawler: NaverCareerCrawler) -> None:
        html_with_pii = """
        <div class="content_detail">
        <p>문의: recruiter@naver.com / 010-1234-5678</p>
        </div>
        """
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=html_with_pii,
            status=200,
        )

        item = {"annoId": "99999", "annoSubject": "테스트 공고"}
        posting = crawler._detail_to_posting(item)

        assert posting is not None
        assert "recruiter@naver.com" not in posting.description_raw
        assert "[EMAIL]" in posting.description_raw
        assert "010-1234-5678" not in posting.description_raw
        assert "[PHONE]" in posting.description_raw


class TestNaverCareerFullCrawl:
    @responses.activate
    def test_full_crawl_pipeline(self, crawler: NaverCareerCrawler) -> None:
        # Mock list endpoint
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        # Second call returns empty (end of pages)
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_EMPTY,
            status=200,
        )
        # Mock detail endpoints
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=MOCK_DETAIL_HTML_20240001,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=MOCK_DETAIL_HTML_20240002,
            status=200,
        )

        postings = crawler.crawl()
        assert len(postings) == 2
        assert all(p.source_platform == "naver_career" for p in postings)
        assert all(p.company_name == "네이버" for p in postings)

    @responses.activate
    def test_deduplicates_by_anno_id(self) -> None:
        crawler = NaverCareerCrawler(max_pages=2, page_size=10)
        # Same items in both pages
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_RESPONSE,
            status=200,
        )
        responses.add(
            responses.POST,
            "https://recruit.navercorp.com/rcrt/loadJobList.do",
            json=MOCK_JOB_LIST_EMPTY,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=MOCK_DETAIL_HTML_20240001,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://recruit.navercorp.com/rcrt/view.do",
            body=MOCK_DETAIL_HTML_20240002,
            status=200,
        )

        postings = crawler.crawl()
        assert len(postings) == 2  # dedup by annoId
