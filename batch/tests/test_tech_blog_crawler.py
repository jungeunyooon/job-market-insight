"""Tests for tech blog crawler."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.tech_blog import TechBlogCrawler, BlogPost, BLOG_CONFIGS


MOCK_RSS_FEED = {
    "bozo": False,
    "entries": [
        {
            "title": "네이버 검색 시스템의 Kafka 도입기",
            "link": "https://d2.naver.com/helloworld/12345",
            "published_parsed": (2025, 6, 15, 10, 0, 0, 0, 0, 0),
            "summary": "네이버 검색에서 Kafka를 도입한 경험을 공유합니다.",
            "tags": [{"term": "Kafka"}, {"term": "Backend"}],
        },
        {
            "title": "Spring Boot 3.0 마이그레이션 가이드",
            "link": "https://d2.naver.com/helloworld/12346",
            "published_parsed": (2024, 3, 1, 8, 0, 0, 0, 0, 0),
            "summary": "Spring Boot 3.0으로 마이그레이션한 과정입니다.",
            "tags": [{"term": "Spring Boot"}, {"term": "Java"}],
        },
        {
            "title": "",  # empty title — skip
            "link": "https://d2.naver.com/helloworld/12347",
        },
    ],
}

MOCK_EMPTY_FEED = {
    "bozo": True,
    "bozo_exception": Exception("Parse error"),
    "entries": [],
}


@pytest.fixture
def crawler() -> TechBlogCrawler:
    return TechBlogCrawler(companies=["네이버"], max_posts_per_company=50)


class TestTechBlogCrawlerInit:
    def test_default_companies(self) -> None:
        crawler = TechBlogCrawler()
        assert len(crawler._companies) == len(BLOG_CONFIGS)

    def test_custom_companies(self) -> None:
        crawler = TechBlogCrawler(companies=["네이버", "카카오"])
        assert crawler._companies == ["네이버", "카카오"]


class TestTechBlogRSSParsing:
    @patch("crawlers.tech_blog.feedparser.parse")
    def test_parses_valid_entries(self, mock_parse: MagicMock, crawler: TechBlogCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]
        mock_parse.return_value.bozo = False

        posts = crawler.crawl()

        assert len(posts) == 2  # 1 invalid entry skipped
        assert posts[0].company_name == "네이버"
        assert posts[0].title == "네이버 검색 시스템의 Kafka 도입기"
        assert posts[0].url == "https://d2.naver.com/helloworld/12345"

    @patch("crawlers.tech_blog.feedparser.parse")
    def test_parses_published_date_and_year(self, mock_parse: MagicMock, crawler: TechBlogCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]
        mock_parse.return_value.bozo = False

        posts = crawler.crawl()

        assert posts[0].published_year == 2025
        assert posts[1].published_year == 2024

    @patch("crawlers.tech_blog.feedparser.parse")
    def test_extracts_tags(self, mock_parse: MagicMock, crawler: TechBlogCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]
        mock_parse.return_value.bozo = False

        posts = crawler.crawl()

        assert posts[0].tags == ["Kafka", "Backend"]
        assert posts[1].tags == ["Spring Boot", "Java"]

    @patch("crawlers.tech_blog.feedparser.parse")
    def test_extracts_content(self, mock_parse: MagicMock, crawler: TechBlogCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]
        mock_parse.return_value.bozo = False

        posts = crawler.crawl()

        assert "Kafka" in posts[0].content_raw

    @patch("crawlers.tech_blog.feedparser.parse")
    def test_empty_feed(self, mock_parse: MagicMock, crawler: TechBlogCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_EMPTY_FEED)
        mock_parse.return_value.entries = []
        mock_parse.return_value.bozo = True

        posts = crawler.crawl()

        assert len(posts) == 0

    @patch("crawlers.tech_blog.feedparser.parse")
    def test_unknown_company_skipped(self, mock_parse: MagicMock) -> None:
        crawler = TechBlogCrawler(companies=["알 수 없는 회사"])
        posts = crawler.crawl()
        assert len(posts) == 0
        mock_parse.assert_not_called()


class TestFetchFullContent:

    def test_fetch_page_content_extracts_article(self):
        """_fetch_page_content extracts text from <article> tag."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)
        html = """<html><body>
        <nav>Menu</nav>
        <article>
        <h1>Kafka 도입기</h1>
        <p>네이버 검색에서 Kafka를 도입한 경험을 공유합니다. 대규모 이벤트 스트리밍을 위해 Kafka를 선택했고, 파티셔닝 전략과 컨슈머 그룹 설계에 대해 설명합니다.</p>
        </article>
        <footer>Copyright</footer>
        </body></html>"""

        with patch.object(crawler._session, 'get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = html
            mock_get.return_value = mock_resp

            result = crawler._fetch_page_content("https://example.com/post")

        assert result is not None
        assert "Kafka 도입기" in result
        assert "파티셔닝 전략" in result
        assert "Menu" not in result  # nav removed
        assert "Copyright" not in result  # footer removed

    def test_fetch_page_content_returns_none_for_short_content(self):
        """Returns None when extracted text is under 100 chars."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)
        html = "<html><body><article><p>Short</p></article></body></html>"

        with patch.object(crawler._session, 'get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = html
            mock_get.return_value = mock_resp

            result = crawler._fetch_page_content("https://example.com/post")

        assert result is None

    def test_fetch_page_content_masks_email(self):
        """PII masking: email addresses are replaced with [EMAIL]."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)
        long_text = "A" * 50
        html = f'<html><body><article><p>{long_text} Contact: user@example.com for details. {long_text}</p></article></body></html>'

        with patch.object(crawler._session, 'get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = html
            mock_get.return_value = mock_resp

            result = crawler._fetch_page_content("https://example.com/post")

        assert result is not None
        assert "[EMAIL]" in result
        assert "user@example.com" not in result

    def test_fetch_page_content_returns_none_on_http_error(self):
        """Returns None when HTTP response is not 200."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)

        with patch.object(crawler._session, 'get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp

            result = crawler._fetch_page_content("https://example.com/post")

        assert result is None

    def test_fetch_page_content_returns_none_on_exception(self):
        """Returns None when request raises an exception."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)

        with patch.object(crawler._session, 'get', side_effect=Exception("Connection error")):
            result = crawler._fetch_page_content("https://example.com/post")

        assert result is None

    @patch("crawlers.tech_blog.time.sleep")
    def test_enrich_replaces_with_longer_content(self, mock_sleep):
        """_enrich_with_full_content replaces RSS summary with longer full content."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)
        short_summary = "짧은 RSS 요약"
        long_content = "A" * 200  # much longer than summary

        posts = [BlogPost(company_name="네이버", title="Test", url="https://example.com/1", content_raw=short_summary)]

        with patch.object(crawler, '_fetch_page_content', return_value=long_content):
            result = crawler._enrich_with_full_content(posts)

        assert result[0].content_raw == long_content
        mock_sleep.assert_called_once_with(1.0)

    @patch("crawlers.tech_blog.time.sleep")
    def test_enrich_keeps_summary_when_fetch_fails(self, mock_sleep):
        """Keeps RSS summary when full content fetch returns None."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)
        original = "원래 RSS 요약 내용"

        posts = [BlogPost(company_name="네이버", title="Test", url="https://example.com/1", content_raw=original)]

        with patch.object(crawler, '_fetch_page_content', return_value=None):
            result = crawler._enrich_with_full_content(posts)

        assert result[0].content_raw == original

    @patch("crawlers.tech_blog.time.sleep")
    @patch("crawlers.tech_blog.feedparser.parse")
    def test_crawl_with_fetch_full_content_calls_enrich(self, mock_parse, mock_sleep):
        """crawl() with fetch_full_content=True calls _enrich_with_full_content."""
        crawler = TechBlogCrawler(companies=["네이버"], fetch_full_content=True)

        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]
        mock_parse.return_value.bozo = False

        with patch.object(crawler, '_enrich_with_full_content', wraps=crawler._enrich_with_full_content) as mock_enrich:
            with patch.object(crawler, '_fetch_page_content', return_value=None):
                posts = crawler.crawl()
            mock_enrich.assert_called_once()
