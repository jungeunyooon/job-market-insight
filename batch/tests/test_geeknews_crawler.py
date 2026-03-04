"""Tests for GeekNews RSS crawler."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.trend.geeknews import GeekNewsCrawler


MOCK_RSS_FEED = {
    "bozo": False,
    "entries": [
        {
            "title": "Rust 1.80 릴리스 — 새로운 기능 정리",
            "link": "https://news.hada.io/topic?id=18001",
            "published_parsed": (2026, 3, 1, 12, 0, 0, 0, 0, 0),
        },
        {
            "title": "LangChain v0.3 — 에이전트 프레임워크 대변화",
            "link": "https://news.hada.io/topic?id=18002",
            "published_parsed": (2026, 3, 2, 8, 30, 0, 0, 0, 0),
        },
        {
            "title": "Kafka 4.0 — KRaft 모드 기본 전환",
            "link": "https://news.hada.io/topic?id=18003",
            "published_parsed": (2026, 3, 3, 15, 0, 0, 0, 0, 0),
        },
        {
            "title": "",  # empty title — should be skipped
            "link": "https://news.hada.io/topic?id=18004",
        },
        {
            "title": "Kubernetes 1.31 릴리스",
            "link": "",  # empty link — should be skipped
        },
    ],
}

MOCK_EMPTY_FEED = {
    "bozo": True,
    "bozo_exception": Exception("Feed parse error"),
    "entries": [],
}


@pytest.fixture
def crawler() -> GeekNewsCrawler:
    return GeekNewsCrawler(max_items=50)


class TestGeekNewsCrawlerInit:
    def test_source_name(self, crawler: GeekNewsCrawler) -> None:
        assert crawler.get_source_name() == "GEEKNEWS"


class TestGeekNewsCrawlParsing:
    @patch("crawlers.trend.geeknews.feedparser.parse")
    def test_parses_valid_entries(self, mock_parse: MagicMock, crawler: GeekNewsCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]

        posts = crawler.crawl()

        assert len(posts) == 3  # 2 invalid entries skipped
        assert posts[0].title == "Rust 1.80 릴리스 — 새로운 기능 정리"
        assert posts[0].source == "GEEKNEWS"
        assert posts[0].external_id == "18001"
        assert posts[0].url == "https://news.hada.io/topic?id=18001"

    @patch("crawlers.trend.geeknews.feedparser.parse")
    def test_parses_published_date(self, mock_parse: MagicMock, crawler: GeekNewsCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]

        posts = crawler.crawl()

        assert posts[0].published_at == datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert posts[1].published_at == datetime(2026, 3, 2, 8, 30, 0, tzinfo=timezone.utc)

    @patch("crawlers.trend.geeknews.feedparser.parse")
    def test_empty_feed_returns_empty(self, mock_parse: MagicMock, crawler: GeekNewsCrawler) -> None:
        mock_parse.return_value = MagicMock(**MOCK_EMPTY_FEED)
        mock_parse.return_value.entries = []
        mock_parse.return_value.bozo = True

        posts = crawler.crawl()

        assert len(posts) == 0

    @patch("crawlers.trend.geeknews.feedparser.parse")
    def test_max_items_limit(self, mock_parse: MagicMock) -> None:
        crawler = GeekNewsCrawler(max_items=2)
        mock_parse.return_value = MagicMock(**MOCK_RSS_FEED)
        mock_parse.return_value.entries = MOCK_RSS_FEED["entries"]

        posts = crawler.crawl()

        assert len(posts) == 2  # limited to max_items=2


class TestGeekNewsExtractId:
    def test_extract_id_from_topic_url(self) -> None:
        assert GeekNewsCrawler._extract_id("https://news.hada.io/topic?id=18001") == "18001"

    def test_extract_id_with_extra_params(self) -> None:
        assert GeekNewsCrawler._extract_id("https://news.hada.io/topic?id=18001&ref=rss") == "18001"

    def test_extract_id_no_id_param(self) -> None:
        assert GeekNewsCrawler._extract_id("https://example.com/article") is None
