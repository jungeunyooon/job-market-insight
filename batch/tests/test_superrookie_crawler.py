"""Tests for SuperRookie crawler."""

import pytest
import responses

from crawlers.superrookie import SuperRookieCrawler, SUPERROOKIE_API_BASE


def _make_job(
    job_id: str = "abc123",
    title: str = "백엔드 개발자",
    company: str = "테스트회사",
    is_ended: bool = False,
    city: str = "서울",
    job_level: str = "신입/경력",
    tags: list | None = None,
    description: str = "Spring Boot 경험자 우대",
    email: str | None = None,
    phone: str | None = None,
) -> dict:
    """헬퍼: SuperRookie API 응답 형태의 job dict 생성."""
    job = {
        "_id": job_id,
        "job_title_decoded": title,
        "company_name_decoded": company,
        "is_ended": is_ended,
        "city": city,
        "job_level": job_level,
        "tags": tags or [],
        "job_description": description,
        "created_at": "2025-12-01T00:00:00Z",
    }
    if email:
        job["job_description"] += f" 문의: {email}"
    if phone:
        job["job_description"] += f" 연락처: {phone}"
    return job


class TestSuperRookieCrawlerInit:
    """크롤러 초기화 테스트."""

    def test_source_name(self):
        crawler = SuperRookieCrawler()
        assert crawler.get_source_name() == "superrookie"

    def test_rate_limit_delay(self):
        crawler = SuperRookieCrawler()
        assert crawler.get_rate_limit_delay() == 1.0

    def test_custom_params(self):
        crawler = SuperRookieCrawler(max_pages=3, page_size=10)
        assert crawler._max_pages == 3
        assert crawler._page_size == 10


class TestFetchJobList:
    """_fetch_job_list 메서드 테스트."""

    @responses.activate
    def test_fetch_job_list_success(self):
        """정상 응답 시 job 리스트를 반환한다."""
        jobs = [_make_job("1"), _make_job("2")]
        responses.add(
            responses.GET,
            SUPERROOKIE_API_BASE,
            json=jobs,
            status=200,
        )

        crawler = SuperRookieCrawler()
        result = crawler._fetch_job_list(page=1)
        assert len(result) == 2

    @responses.activate
    def test_fetch_job_list_dict_response(self):
        """응답이 dict with results key인 경우도 처리한다."""
        jobs = [_make_job("1")]
        responses.add(
            responses.GET,
            SUPERROOKIE_API_BASE,
            json={"results": jobs, "total": 1},
            status=200,
        )

        crawler = SuperRookieCrawler()
        result = crawler._fetch_job_list(page=1)
        assert len(result) == 1

    @responses.activate
    def test_fetch_job_list_server_error(self):
        """서버 에러 시 빈 리스트를 반환한다."""
        responses.add(
            responses.GET,
            SUPERROOKIE_API_BASE,
            status=500,
        )

        crawler = SuperRookieCrawler()
        result = crawler._fetch_job_list(page=1)
        assert result == []

    @responses.activate
    def test_fetch_job_list_network_error(self):
        """네트워크 에러 시 빈 리스트를 반환한다."""
        responses.add(
            responses.GET,
            SUPERROOKIE_API_BASE,
            body=ConnectionError("connection refused"),
        )

        crawler = SuperRookieCrawler()
        result = crawler._fetch_job_list(page=1)
        assert result == []


class TestFullCrawl:
    """전체 crawl() 메서드 테스트."""

    @responses.activate
    def test_crawl_single_page(self):
        """단일 페이지 크롤링."""
        jobs = [_make_job("1", title="백엔드"), _make_job("2", title="프론트엔드")]
        responses.add(
            responses.GET,
            SUPERROOKIE_API_BASE,
            json=jobs,
            status=200,
        )

        crawler = SuperRookieCrawler(max_pages=1, page_size=20)
        postings = crawler.crawl()
        assert len(postings) == 2
        assert postings[0].title == "백엔드"
        assert postings[0].source_platform == "superrookie"

    @responses.activate
    def test_crawl_multiple_pages(self):
        """여러 페이지 크롤링 - 마지막 페이지가 page_size보다 적으면 중단."""
        page1 = [_make_job(f"p1_{i}") for i in range(5)]
        page2 = [_make_job(f"p2_{i}") for i in range(3)]  # 5보다 적음 → 마지막

        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=page1, status=200)
        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=page2, status=200)

        crawler = SuperRookieCrawler(max_pages=5, page_size=5)
        postings = crawler.crawl()
        assert len(postings) == 8

    @responses.activate
    def test_crawl_deduplication(self):
        """중복 job_id는 한 번만 수집한다."""
        jobs = [_make_job("same_id"), _make_job("same_id"), _make_job("other_id")]
        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=jobs, status=200)

        crawler = SuperRookieCrawler(max_pages=1, page_size=20)
        postings = crawler.crawl()
        assert len(postings) == 2

    @responses.activate
    def test_crawl_includes_ended_postings(self):
        """마감된 공고(is_ended=True)도 수집한다."""
        jobs = [
            _make_job("active", is_ended=False),
            _make_job("ended", is_ended=True, title="마감 공고"),
        ]
        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=jobs, status=200)

        crawler = SuperRookieCrawler(max_pages=1, page_size=20)
        postings = crawler.crawl()
        assert len(postings) == 2
        ended = [p for p in postings if "마감" in p.description_raw]
        assert len(ended) == 1

    @responses.activate
    def test_crawl_empty_response(self):
        """빈 응답 시 빈 리스트를 반환한다."""
        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=[], status=200)

        crawler = SuperRookieCrawler(max_pages=1)
        postings = crawler.crawl()
        assert postings == []


class TestPIIMasking:
    """PII 마스킹 테스트."""

    @responses.activate
    def test_email_masked(self):
        """이메일이 [EMAIL]로 마스킹된다."""
        jobs = [_make_job("1", email="test@example.com")]
        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=jobs, status=200)

        crawler = SuperRookieCrawler(max_pages=1)
        postings = crawler.crawl()
        assert len(postings) == 1
        assert "test@example.com" not in postings[0].description_raw
        assert "[EMAIL]" in postings[0].description_raw

    @responses.activate
    def test_phone_masked(self):
        """전화번호가 [PHONE]으로 마스킹된다."""
        jobs = [_make_job("1", phone="010-1234-5678")]
        responses.add(responses.GET, SUPERROOKIE_API_BASE, json=jobs, status=200)

        crawler = SuperRookieCrawler(max_pages=1)
        postings = crawler.crawl()
        assert len(postings) == 1
        assert "010-1234-5678" not in postings[0].description_raw
        assert "[PHONE]" in postings[0].description_raw

    def test_mask_pii_static(self):
        """정적 메서드로 PII 마스킹 직접 테스트."""
        text = "문의: hr@company.com 또는 02-123-4567"
        result = SuperRookieCrawler._mask_pii(text)
        assert "[EMAIL]" in result
        assert "[PHONE]" in result
        assert "hr@company.com" not in result


class TestJobToPosting:
    """_job_to_posting 변환 테스트."""

    def test_basic_conversion(self):
        crawler = SuperRookieCrawler()
        job = _make_job("test1", title="백엔드 개발자", company="좋은회사", city="서울")
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.title == "백엔드 개발자"
        assert posting.company_name == "좋은회사"
        assert posting.source_platform == "superrookie"
        assert "test1" in posting.source_url
        assert posting.location == "서울"

    def test_missing_title_returns_none(self):
        crawler = SuperRookieCrawler()
        job = _make_job("test1")
        job["job_title_decoded"] = ""
        job["job_title"] = ""
        posting = crawler._job_to_posting(job)
        assert posting is None

    def test_missing_company_returns_none(self):
        crawler = SuperRookieCrawler()
        job = _make_job("test1")
        job["company_name_decoded"] = ""
        job["company_name"] = ""
        posting = crawler._job_to_posting(job)
        assert posting is None

    def test_tags_extraction(self):
        crawler = SuperRookieCrawler()
        job = _make_job("test1", tags=["Python", "Django", "AWS"])
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert "Python" in posting.tags
        assert "Django" in posting.tags

    def test_date_parsing(self):
        crawler = SuperRookieCrawler()
        job = _make_job("test1")
        job["created_at"] = "2025-12-01T00:00:00Z"
        posting = crawler._job_to_posting(job)

        assert posting is not None
        assert posting.posted_at is not None
        assert posting.posted_at.year == 2025
        assert posting.posted_at.month == 12


class TestDateParsing:
    """_parse_date 정적 메서드 테스트."""

    def test_iso_format_with_ms(self):
        result = SuperRookieCrawler._parse_date("2025-06-15T10:30:00.000Z")
        assert result is not None
        assert result.year == 2025

    def test_iso_format_without_ms(self):
        result = SuperRookieCrawler._parse_date("2025-06-15T10:30:00Z")
        assert result is not None

    def test_date_only(self):
        result = SuperRookieCrawler._parse_date("2025-06-15")
        assert result is not None

    def test_none_input(self):
        assert SuperRookieCrawler._parse_date(None) is None

    def test_invalid_format(self):
        assert SuperRookieCrawler._parse_date("not-a-date") is None
