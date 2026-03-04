"""dev.to Forem API crawler for developer trend tracking.

Uses the Forem public API:
  https://dev.to/api/articles
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from crawlers.trend.base import TrendCrawler, TrendPost

logger = logging.getLogger(__name__)

DEVTO_API_URL = "https://dev.to/api/articles"
_REQUEST_TIMEOUT = 10  # seconds


class DevToCrawler(TrendCrawler):
    """Crawler for dev.to articles via the Forem public API."""

    def __init__(
        self,
        api_url: str = DEVTO_API_URL,
        tag: str = "programming",
        max_items: int = 30,
    ) -> None:
        self._api_url = api_url
        self._tag = tag
        self._max_items = max_items

    def get_source_name(self) -> str:
        return "DEVTO"

    def crawl(self) -> list[TrendPost]:
        """Fetch dev.to articles and return as TrendPost list."""
        logger.info(f"Fetching dev.to articles (tag={self._tag})")
        articles = self._fetch_articles(page=1)

        posts: list[TrendPost] = []
        for article in articles[: self._max_items]:
            post = self._article_to_post(article)
            if post:
                posts.append(post)

        logger.info(f"Collected {len(posts)} posts from dev.to")
        return posts

    def _fetch_articles(self, page: int = 1) -> list[dict]:
        """Fetch a page of articles from the Forem API."""
        params = {
            "tag": self._tag,
            "per_page": self._max_items,
            "page": page,
        }
        try:
            resp = requests.get(self._api_url, params=params, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error(f"Failed to fetch dev.to articles: {exc}")
            return []

    def _article_to_post(self, article: dict) -> TrendPost | None:
        """Convert a Forem API article dict to TrendPost."""
        title = (article.get("title") or "").strip()
        url = (article.get("url") or "").strip()

        if not title or not url:
            return None

        article_id = article["id"]
        score = article.get("positive_reactions_count", 0) or 0
        comment_count = article.get("comments_count", 0) or 0

        published_at: datetime | None = None
        raw_date = article.get("published_at")
        if raw_date:
            try:
                # Forem returns ISO 8601: "2025-03-01T12:00:00.000Z"
                published_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                # Normalise to UTC with no sub-second precision
                published_at = published_at.astimezone(timezone.utc).replace(microsecond=0)
            except (ValueError, AttributeError):
                pass

        return TrendPost(
            source="DEVTO",
            external_id=str(article_id),
            title=title,
            url=url,
            score=score,
            comment_count=comment_count,
            published_at=published_at,
        )
