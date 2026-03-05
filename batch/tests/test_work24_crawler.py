"""Tests for Work24 (워크넷) OpenAPI crawler.

TDD: These tests define the expected behavior of Work24Crawler.
Uses responses library to mock HTTP requests — never hits real API.
"""

import sys
from pathlib import Path

import pytest
import responses

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.work24 import Work24Crawler


MOCK_XML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<wantedRoot>
    <wanted>
        <company>카카오</company>
        <title>백엔드 개발자</title>
        <sal>5000만원</sal>
        <salTpNm>연봉</salTpNm>
        <region>서울 강남구</region>
        <holidayTpNm>정규직</holidayTpNm>
        <career>경력 3년 이상</career>
        <minEdubg>대졸</minEdubg>
        <wantedInfoUrl>https://www.work24.go.kr/wk/a/b/1200/dtlRecrContents.do?wantedAuthNo=K123</wantedInfoUrl>
        <regDt>2026-02-15</regDt>
        <closeDt>2026-03-31</closeDt>
        <wantedAuthNo>K123</wantedAuthNo>
        <jobsCd>024</jobsCd>
        <jobCont>Spring Boot 기반 API 서버 개발 및 운영</jobCont>
        <reqCareer>Java, Spring Boot 경험 필수</reqCareer>
        <prefCond>AWS, Docker, Kubernetes 경험 우대</prefCond>
        <welfare>자율 출퇴근, 원격 근무 가능</welfare>
        <enterTpNm>주 5일 근무</enterTpNm>
    </wanted>
    <wanted>
        <company>배달의민족</company>
        <title>서버 엔지니어</title>
        <region>서울 송파구</region>
        <holidayTpNm>정규직</holidayTpNm>
        <career>경력무관</career>
        <wantedInfoUrl>https://www.work24.go.kr/wk/a/b/1200/dtlRecrContents.do?wantedAuthNo=K456</wantedInfoUrl>
        <regDt>2026-02-20</regDt>
        <wantedAuthNo>K456</wantedAuthNo>
        <jobsCd>024</jobsCd>
    </wanted>
</wantedRoot>"""

MOCK_XML_EMPTY = """<?xml version="1.0" encoding="UTF-8"?><wantedRoot></wantedRoot>"""


@pytest.fixture
def crawler() -> Work24Crawler:
    return Work24Crawler(api_key="test-api-key", max_count=50)


@pytest.fixture
def crawler_no_key() -> Work24Crawler:
    return Work24Crawler(api_key="", max_count=50)


class TestWork24Init:
    def test_source_name(self, crawler: Work24Crawler) -> None:
        assert crawler.get_source_name() == "work24"

    def test_rate_limit(self, crawler: Work24Crawler) -> None:
        assert crawler.get_rate_limit_delay() >= 1.0


class TestWork24NoApiKey:
    def test_graceful_skip_without_api_key(self, crawler_no_key: Work24Crawler) -> None:
        """API 키 없으면 빈 리스트 반환, 에러 없음."""
        postings = crawler_no_key.crawl()
        assert postings == []


class TestWork24XmlParsing:
    def test_parse_xml_response(self, crawler: Work24Crawler) -> None:
        items = crawler._parse_xml_response(MOCK_XML_RESPONSE)
        assert len(items) == 2
        assert items[0]["company_name"] == "카카오"
        assert items[0]["title"] == "백엔드 개발자"
        assert items[0]["location"] == "서울 강남구"
        assert items[0]["requirements"] == "Java, Spring Boot 경험 필수"
        assert items[0]["preferred"] == "AWS, Docker, Kubernetes 경험 우대"
        assert items[0]["benefits"] == "자율 출퇴근, 원격 근무 가능"
        assert items[0]["responsibilities"] == "Spring Boot 기반 API 서버 개발 및 운영"
        assert items[1]["company_name"] == "배달의민족"

    def test_parse_empty_xml(self, crawler: Work24Crawler) -> None:
        items = crawler._parse_xml_response(MOCK_XML_EMPTY)
        assert items == []

    def test_parse_invalid_xml(self, crawler: Work24Crawler) -> None:
        items = crawler._parse_xml_response("not valid xml")
        assert items == []


class TestWork24ItemToPosting:
    def test_converts_to_raw_posting_with_structured_fields(self, crawler: Work24Crawler) -> None:
        items = crawler._parse_xml_response(MOCK_XML_RESPONSE)
        posting = crawler._item_to_posting(items[0])

        assert posting is not None
        assert posting.title == "백엔드 개발자"
        assert posting.company_name == "카카오"
        assert posting.source_platform == "work24"
        assert "work24" in posting.source_url
        assert posting.location == "서울 강남구"
        assert posting.employment_type == "정규직"

        # 구조화 필드 확인
        assert posting.requirements_raw is not None
        assert "Java" in posting.requirements_raw
        assert posting.preferred_raw is not None
        assert "AWS" in posting.preferred_raw
        assert posting.responsibilities_raw is not None
        assert "Spring Boot" in posting.responsibilities_raw
        assert posting.benefits_raw is not None
        assert "원격" in posting.benefits_raw
        assert posting.work_type is not None

    def test_handles_minimal_item(self, crawler: Work24Crawler) -> None:
        """최소 필드만 있는 공고도 처리."""
        items = crawler._parse_xml_response(MOCK_XML_RESPONSE)
        posting = crawler._item_to_posting(items[1])

        assert posting is not None
        assert posting.title == "서버 엔지니어"
        assert posting.company_name == "배달의민족"
        # career 필드가 requirements_raw 폴백으로 사용됨
        assert posting.requirements_raw == "경력무관"
        # 전용 필드가 없는 것은 None
        assert posting.preferred_raw is None
        assert posting.responsibilities_raw is None

    def test_skips_empty_title(self, crawler: Work24Crawler) -> None:
        item = {"title": "", "company_name": "Foo"}
        posting = crawler._item_to_posting(item)
        assert posting is None


class TestWork24FullCrawl:
    @responses.activate
    def test_full_crawl_pipeline(self, crawler: Work24Crawler) -> None:
        responses.add(
            responses.GET,
            "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSrch.do",
            body=MOCK_XML_RESPONSE,
            status=200,
            content_type="application/xml",
        )

        postings = crawler.crawl()
        assert len(postings) == 2
        assert postings[0].company_name == "카카오"
        assert postings[1].company_name == "배달의민족"
        assert all(p.source_platform == "work24" for p in postings)

    @responses.activate
    def test_handles_api_error(self, crawler: Work24Crawler) -> None:
        responses.add(
            responses.GET,
            "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSrch.do",
            status=500,
        )

        postings = crawler.crawl()
        assert postings == []

    @responses.activate
    def test_handles_auth_error(self, crawler: Work24Crawler) -> None:
        responses.add(
            responses.GET,
            "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSrch.do",
            status=401,
        )

        postings = crawler.crawl()
        assert postings == []


class TestWork24PiiMasking:
    def test_masks_email_and_phone(self, crawler: Work24Crawler) -> None:
        item = {
            "title": "개발자",
            "company_name": "테스트",
            "url": "https://example.com",
            "responsibilities": "연락: hr@test.com 또는 02-1234-5678",
        }
        posting = crawler._item_to_posting(item)
        assert posting is not None
        assert "hr@test.com" not in posting.description_raw
        assert "[EMAIL]" in posting.description_raw
        assert "02-1234-5678" not in posting.description_raw
        assert "[PHONE]" in posting.description_raw
