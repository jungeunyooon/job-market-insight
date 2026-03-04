"""Tests for HackerNews Firebase API crawler."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import responses as responses_lib

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.trend.hackernews import HackerNewsCrawler

HN_BASE = "https://hacker-news.firebaseio.com/v0"

MOCK_TOP_STORIES = [101, 102, 103, 104, 105]

MOCK_ITEM_101 = {
    "id": 101,
    "type": "story",
    "title": "Show HN: I built a Rust async runtime from scratch",
    "url": "https://example.com/rust-runtime",
    "score": 342,
    "descendants": 87,
    "time": 1740830400,  # 2025-03-01 12:00:00 UTC
    "by": "rustdev",
}

MOCK_ITEM_102 = {
    "id": 102,
    "type": "story",
    "title": "Postgres 17 Released",
    "url": "https://postgresql.org/news/17",
    "score": 512,
    "descendants": 143,
    "time": 1740912000,
    "by": "pgfan",
}

MOCK_ITEM_103 = {
    "id": 103,
    "type": "job",  # non-story type — should be skipped
    "title": "Senior Engineer at ACME",
    "url": "https://acme.com/jobs",
    "score": 0,
    "time": 1740998400,
    "by": "acme_hr",
}

MOCK_ITEM_104 = {
    "id": 104,
    "type": "story",
    "title": "",  # empty title — should be skipped
    "url": "https://example.com/empty",
    "score": 10,
    "time": 1740998400,
    "by": "anon",
}

MOCK_ITEM_105 = {
    "id": 105,
    "type": "story",
    "title": "Ask HN: What stack do you use in 2025?",
    # no url — Ask HN posts often lack url
    "score": 200,
    "descendants": 50,
    "time": 1741084800,
    "by": "curious_dev",
}


@pytest.fixture
def crawler() -> HackerNewsCrawler:
    return HackerNewsCrawler(max_items=10)


class TestHackerNewsCrawlerInit:
    def test_source_name(self, crawler: HackerNewsCrawler) -> None:
        assert crawler.get_source_name() == "HN"

    def test_default_max_items(self) -> None:
        c = HackerNewsCrawler()
        assert c._max_items == 30

    def test_custom_max_items(self) -> None:
        c = HackerNewsCrawler(max_items=5)
        assert c._max_items == 5

    def test_base_url(self, crawler: HackerNewsCrawler) -> None:
        assert crawler._base_url == HN_BASE


class TestHackerNewsFetchTopStories:
    @responses_lib.activate
    def test_fetch_top_stories_returns_list(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            json=MOCK_TOP_STORIES,
            status=200,
        )
        story_ids = crawler._fetch_top_story_ids()
        assert story_ids == MOCK_TOP_STORIES

    @responses_lib.activate
    def test_fetch_top_stories_http_error_returns_empty(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            status=500,
        )
        story_ids = crawler._fetch_top_story_ids()
        assert story_ids == []

    @responses_lib.activate
    def test_fetch_top_stories_network_error_returns_empty(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            body=Exception("Network error"),
        )
        story_ids = crawler._fetch_top_story_ids()
        assert story_ids == []


class TestHackerNewsFetchItem:
    @responses_lib.activate
    def test_fetch_item_returns_dict(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/101.json",
            json=MOCK_ITEM_101,
            status=200,
        )
        item = crawler._fetch_item(101)
        assert item is not None
        assert item["id"] == 101
        assert item["title"] == "Show HN: I built a Rust async runtime from scratch"

    @responses_lib.activate
    def test_fetch_item_http_error_returns_none(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/999.json",
            status=404,
        )
        item = crawler._fetch_item(999)
        assert item is None

    @responses_lib.activate
    def test_fetch_item_network_error_returns_none(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/999.json",
            body=Exception("timeout"),
        )
        item = crawler._fetch_item(999)
        assert item is None


class TestHackerNewsItemToPost:
    def test_converts_story_with_url(self, crawler: HackerNewsCrawler) -> None:
        post = crawler._item_to_post(MOCK_ITEM_101)
        assert post is not None
        assert post.source == "HN"
        assert post.external_id == "101"
        assert post.title == "Show HN: I built a Rust async runtime from scratch"
        assert post.url == "https://example.com/rust-runtime"
        assert post.score == 342
        assert post.comment_count == 87

    def test_converts_published_at_from_unix_time(self, crawler: HackerNewsCrawler) -> None:
        post = crawler._item_to_post(MOCK_ITEM_101)
        assert post is not None
        assert post.published_at == datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_skips_non_story_type(self, crawler: HackerNewsCrawler) -> None:
        post = crawler._item_to_post(MOCK_ITEM_103)
        assert post is None

    def test_skips_empty_title(self, crawler: HackerNewsCrawler) -> None:
        post = crawler._item_to_post(MOCK_ITEM_104)
        assert post is None

    def test_ask_hn_uses_hn_url_fallback(self, crawler: HackerNewsCrawler) -> None:
        post = crawler._item_to_post(MOCK_ITEM_105)
        assert post is not None
        assert post.url == f"https://news.ycombinator.com/item?id=105"

    def test_comment_count_defaults_to_zero_when_missing(self, crawler: HackerNewsCrawler) -> None:
        item = {**MOCK_ITEM_101}
        del item["descendants"]
        post = crawler._item_to_post(item)
        assert post is not None
        assert post.comment_count == 0


class TestHackerNewsCrawlPipeline:
    @responses_lib.activate
    def test_full_crawl_returns_valid_posts(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            json=[101, 102],
            status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/101.json",
            json=MOCK_ITEM_101,
            status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/102.json",
            json=MOCK_ITEM_102,
            status=200,
        )

        posts = crawler.crawl()

        assert len(posts) == 2
        assert posts[0].external_id == "101"
        assert posts[1].external_id == "102"

    @responses_lib.activate
    def test_crawl_skips_failed_item_fetches(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            json=[101, 999],
            status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/101.json",
            json=MOCK_ITEM_101,
            status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/999.json",
            status=500,
        )

        posts = crawler.crawl()

        assert len(posts) == 1
        assert posts[0].external_id == "101"

    @responses_lib.activate
    def test_crawl_respects_max_items(self) -> None:
        crawler = HackerNewsCrawler(max_items=2)
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            json=[101, 102, 103],
            status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/101.json",
            json=MOCK_ITEM_101,
            status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/item/102.json",
            json=MOCK_ITEM_102,
            status=200,
        )

        posts = crawler.crawl()

        assert len(posts) == 2

    @responses_lib.activate
    def test_crawl_returns_empty_when_top_stories_fails(self, crawler: HackerNewsCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            f"{HN_BASE}/topstories.json",
            status=503,
        )

        posts = crawler.crawl()

        assert posts == []
