"""Tests for dev.to Forem API crawler."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import responses as responses_lib

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawlers.trend.devto import DevToCrawler

DEVTO_API_URL = "https://dev.to/api/articles"

MOCK_ARTICLES = [
    {
        "id": 2001,
        "title": "Building a REST API with FastAPI",
        "url": "https://dev.to/alice/building-rest-api-fastapi-abc1",
        "positive_reactions_count": 215,
        "comments_count": 34,
        "published_at": "2025-03-01T12:00:00.000Z",
        "tag_list": ["python", "fastapi", "webdev"],
        "user": {"username": "alice"},
    },
    {
        "id": 2002,
        "title": "Understanding Rust Ownership",
        "url": "https://dev.to/bob/rust-ownership-xyz2",
        "positive_reactions_count": 432,
        "comments_count": 67,
        "published_at": "2025-03-02T08:30:00.000Z",
        "tag_list": ["rust", "systems"],
        "user": {"username": "bob"},
    },
    {
        "id": 2003,
        "title": "Docker Best Practices 2025",
        "url": "https://dev.to/charlie/docker-best-practices-2025-def3",
        "positive_reactions_count": 88,
        "comments_count": 12,
        "published_at": "2025-03-03T15:45:00.000Z",
        "tag_list": ["docker", "devops"],
        "user": {"username": "charlie"},
    },
]

MOCK_ARTICLE_NO_TITLE = {
    "id": 2004,
    "title": "",
    "url": "https://dev.to/anon/no-title-ghi4",
    "positive_reactions_count": 5,
    "comments_count": 0,
    "published_at": "2025-03-04T10:00:00.000Z",
    "tag_list": [],
    "user": {"username": "anon"},
}

MOCK_ARTICLE_NO_URL = {
    "id": 2005,
    "title": "Article With No URL",
    "url": "",
    "positive_reactions_count": 10,
    "comments_count": 1,
    "published_at": "2025-03-04T11:00:00.000Z",
    "tag_list": ["misc"],
    "user": {"username": "noone"},
}


@pytest.fixture
def crawler() -> DevToCrawler:
    return DevToCrawler(max_items=30)


class TestDevToCrawlerInit:
    def test_source_name(self, crawler: DevToCrawler) -> None:
        assert crawler.get_source_name() == "DEVTO"

    def test_default_max_items(self) -> None:
        c = DevToCrawler()
        assert c._max_items == 30

    def test_custom_max_items(self) -> None:
        c = DevToCrawler(max_items=10)
        assert c._max_items == 10

    def test_default_tag(self) -> None:
        c = DevToCrawler()
        assert c._tag == "programming"

    def test_custom_tag(self) -> None:
        c = DevToCrawler(tag="python")
        assert c._tag == "python"

    def test_api_url(self, crawler: DevToCrawler) -> None:
        assert crawler._api_url == DEVTO_API_URL


class TestDevToFetchArticles:
    @responses_lib.activate
    def test_fetch_articles_returns_list(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            json=MOCK_ARTICLES,
            status=200,
        )
        articles = crawler._fetch_articles(page=1)
        assert len(articles) == 3
        assert articles[0]["id"] == 2001

    @responses_lib.activate
    def test_fetch_articles_passes_correct_params(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            json=MOCK_ARTICLES,
            status=200,
        )
        crawler._fetch_articles(page=2)
        req = responses_lib.calls[0].request
        assert "tag=programming" in req.url
        assert "page=2" in req.url
        assert "per_page=" in req.url

    @responses_lib.activate
    def test_fetch_articles_http_error_returns_empty(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            status=500,
        )
        articles = crawler._fetch_articles(page=1)
        assert articles == []

    @responses_lib.activate
    def test_fetch_articles_network_error_returns_empty(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            body=Exception("Connection reset"),
        )
        articles = crawler._fetch_articles(page=1)
        assert articles == []

    @responses_lib.activate
    def test_fetch_articles_rate_limit_returns_empty(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            status=429,
        )
        articles = crawler._fetch_articles(page=1)
        assert articles == []


class TestDevToArticleToPost:
    def test_converts_article_to_post(self, crawler: DevToCrawler) -> None:
        post = crawler._article_to_post(MOCK_ARTICLES[0])
        assert post is not None
        assert post.source == "DEVTO"
        assert post.external_id == "2001"
        assert post.title == "Building a REST API with FastAPI"
        assert post.url == "https://dev.to/alice/building-rest-api-fastapi-abc1"
        assert post.score == 215
        assert post.comment_count == 34

    def test_converts_published_at_iso8601(self, crawler: DevToCrawler) -> None:
        post = crawler._article_to_post(MOCK_ARTICLES[0])
        assert post is not None
        assert post.published_at == datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_skips_empty_title(self, crawler: DevToCrawler) -> None:
        post = crawler._article_to_post(MOCK_ARTICLE_NO_TITLE)
        assert post is None

    def test_skips_empty_url(self, crawler: DevToCrawler) -> None:
        post = crawler._article_to_post(MOCK_ARTICLE_NO_URL)
        assert post is None

    def test_missing_published_at_defaults_to_none(self, crawler: DevToCrawler) -> None:
        article = {**MOCK_ARTICLES[0], "published_at": None}
        post = crawler._article_to_post(article)
        assert post is not None
        assert post.published_at is None

    def test_invalid_published_at_defaults_to_none(self, crawler: DevToCrawler) -> None:
        article = {**MOCK_ARTICLES[0], "published_at": "not-a-date"}
        post = crawler._article_to_post(article)
        assert post is not None
        assert post.published_at is None


class TestDevToCrawlPipeline:
    @responses_lib.activate
    def test_full_crawl_returns_valid_posts(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            json=MOCK_ARTICLES,
            status=200,
        )

        posts = crawler.crawl()

        assert len(posts) == 3
        assert posts[0].source == "DEVTO"
        assert posts[0].external_id == "2001"

    @responses_lib.activate
    def test_crawl_skips_invalid_articles(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            json=[MOCK_ARTICLES[0], MOCK_ARTICLE_NO_TITLE, MOCK_ARTICLE_NO_URL],
            status=200,
        )

        posts = crawler.crawl()

        assert len(posts) == 1
        assert posts[0].external_id == "2001"

    @responses_lib.activate
    def test_crawl_returns_empty_on_api_failure(self, crawler: DevToCrawler) -> None:
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            status=503,
        )

        posts = crawler.crawl()

        assert posts == []

    @responses_lib.activate
    def test_crawl_respects_max_items(self) -> None:
        crawler = DevToCrawler(max_items=2)
        responses_lib.add(
            responses_lib.GET,
            DEVTO_API_URL,
            json=MOCK_ARTICLES,  # 3 articles
            status=200,
        )

        posts = crawler.crawl()

        assert len(posts) == 2
