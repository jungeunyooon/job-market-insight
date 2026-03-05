"""Tests for Saramin OpenAPI crawler.

TDD: These tests define the expected behavior of SaraminAPICrawler.
Uses responses library to mock HTTP requests — never hits real API.
"""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.saramin import SaraminAPICrawler


MOCK_XML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<jobs>
    <job url="https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=12345">
        <position>
            <title>백엔드 개발자</title>
            <industry>
                <name>IT/인터넷</name>
            </industry>
            <location>
                <name>서울 강남구</name>
            </location>
            <job-type>
                <name>정규직</name>
            </job-type>
            <experience-level>
                <name>경력 3~5년</name>
            </experience-level>
            <required-education-level>
                <name>대졸</name>
            </required-education-level>
        </position>
        <company>
            <detail>
                <name>토스</name>
                <href>https://www.saramin.co.kr/company/toss</href>
            </detail>
        </company>
        <posting-date>2026-02-15</posting-date>
        <expiration-date>2026-03-15</expiration-date>
        <salary>
            <name>5000만원 이상</name>
        </salary>
        <keyword>Java, Spring Boot, Kotlin, AWS</keyword>
    </job>
    <job url="https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=12346">
        <position>
            <title>서버 엔지니어</title>
            <industry>
                <name>IT/인터넷</name>
            </industry>
            <location>
                <name>서울 송파구</name>
            </location>
            <job-type>
                <name>정규직</name>
            </job-type>
            <experience-level>
                <name>경력 1~3년</name>
            </experience-level>
            <required-education-level>
                <name>대졸</name>
            </required-education-level>
        </position>
        <company>
            <detail>
                <name>당근</name>
            </detail>
        </company>
        <posting-date>2026-02-20</posting-date>
        <keyword>Go, Kubernetes, Docker</keyword>
    </job>
</jobs>"""

MOCK_XML_EMPTY = """<?xml version="1.0" encoding="UTF-8"?><jobs></jobs>"""


@pytest.fixture
def crawler() -> SaraminAPICrawler:
    return SaraminAPICrawler(api_key="test-api-key", keywords=["백엔드"], max_count=50)


@pytest.fixture
def crawler_no_key() -> SaraminAPICrawler:
    return SaraminAPICrawler(api_key="", keywords=["백엔드"])


class TestSaraminInit:
    def test_source_name(self, crawler: SaraminAPICrawler) -> None:
        assert crawler.get_source_name() == "saramin"

    def test_rate_limit(self, crawler: SaraminAPICrawler) -> None:
        assert crawler.get_rate_limit_delay() >= 1.0


class TestSaraminNoApiKey:
    def test_graceful_skip_without_api_key(self, crawler_no_key: SaraminAPICrawler) -> None:
        """API 키 없으면 빈 리스트 반환, 에러 없음."""
        postings = crawler_no_key.crawl()
        assert postings == []


class TestSaraminXmlParsing:
    def test_parse_xml_response(self, crawler: SaraminAPICrawler) -> None:
        items = crawler._parse_xml_response(MOCK_XML_RESPONSE)
        assert len(items) == 2
        assert items[0]["title"] == "백엔드 개발자"
        assert items[0]["company_name"] == "토스"
        assert items[0]["location"] == "서울 강남구"
        assert items[0]["keywords"] == "Java, Spring Boot, Kotlin, AWS"
        assert items[1]["company_name"] == "당근"

    def test_parse_empty_xml(self, crawler: SaraminAPICrawler) -> None:
        items = crawler._parse_xml_response(MOCK_XML_EMPTY)
        assert items == []

    def test_parse_invalid_xml(self, crawler: SaraminAPICrawler) -> None:
        items = crawler._parse_xml_response("not valid xml at all")
        assert items == []


class TestSaraminItemToPosting:
    def test_converts_to_raw_posting(self, crawler: SaraminAPICrawler) -> None:
        items = crawler._parse_xml_response(MOCK_XML_RESPONSE)
        posting = crawler._item_to_posting(items[0])

        assert posting is not None
        assert posting.title == "백엔드 개발자"
        assert posting.company_name == "토스"
        assert posting.source_platform == "saramin"
        assert "saramin" in posting.source_url
        assert posting.location == "서울 강남구"
        assert posting.employment_type == "정규직"

        # 기술스택 구조화 필드
        assert posting.tech_stack_raw is not None
        assert "Java" in posting.tech_stack_raw
        assert "Spring Boot" in posting.tech_stack_raw
        assert len(posting.tags) == 4

    def test_skips_empty_title(self, crawler: SaraminAPICrawler) -> None:
        item = {"title": "", "company_name": "Foo"}
        posting = crawler._item_to_posting(item)
        assert posting is None

    def test_skips_empty_company(self, crawler: SaraminAPICrawler) -> None:
        item = {"title": "Job", "company_name": ""}
        posting = crawler._item_to_posting(item)
        assert posting is None


class TestSaraminFullCrawl:
    @responses.activate
    def test_full_crawl_pipeline(self, crawler: SaraminAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://oapi.saramin.co.kr/job-search",
            body=MOCK_XML_RESPONSE,
            status=200,
            content_type="application/xml",
        )

        postings = crawler.crawl()
        assert len(postings) == 2
        assert postings[0].company_name == "토스"
        assert postings[1].company_name == "당근"
        assert all(p.source_platform == "saramin" for p in postings)

    @responses.activate
    def test_handles_api_error(self, crawler: SaraminAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://oapi.saramin.co.kr/job-search",
            status=500,
        )

        postings = crawler.crawl()
        assert postings == []

    @responses.activate
    def test_handles_auth_error(self, crawler: SaraminAPICrawler) -> None:
        responses.add(
            responses.GET,
            "https://oapi.saramin.co.kr/job-search",
            status=401,
        )

        postings = crawler.crawl()
        assert postings == []

    @responses.activate
    def test_deduplicates_across_keywords(self) -> None:
        crawler = SaraminAPICrawler(api_key="test-key", keywords=["백엔드", "서버개발"])
        # Both keywords return same jobs
        responses.add(
            responses.GET,
            "https://oapi.saramin.co.kr/job-search",
            body=MOCK_XML_RESPONSE,
            status=200,
            content_type="application/xml",
        )
        responses.add(
            responses.GET,
            "https://oapi.saramin.co.kr/job-search",
            body=MOCK_XML_RESPONSE,
            status=200,
            content_type="application/xml",
        )

        postings = crawler.crawl()
        assert len(postings) == 2  # dedup by URL
