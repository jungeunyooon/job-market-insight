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
