"""GeekNews RSS crawler for developer trend tracking.

GeekNews (https://news.hada.io) is a Korean developer news curation site.
Uses RSS feed for structured data collection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import feedparser

from crawlers.trend.base import TrendCrawler, TrendPost

logger = logging.getLogger(__name__)

GEEKNEWS_RSS_URL = "https://news.hada.io/rss/news"


class GeekNewsCrawler(TrendCrawler):
    """Crawler for GeekNews RSS feed."""

    def __init__(self, rss_url: str = GEEKNEWS_RSS_URL, max_items: int = 100) -> None:
        self._rss_url = rss_url
        self._max_items = max_items

    def get_source_name(self) -> str:
        return "GEEKNEWS"

    def crawl(self) -> list[TrendPost]:
        """Fetch and parse GeekNews RSS feed.

        Returns list of TrendPost from the RSS entries.
        """
        logger.info(f"Fetching GeekNews RSS from {self._rss_url}")
        feed = feedparser.parse(self._rss_url)

        if feed.bozo and not feed.entries:
            logger.error(f"RSS parse error: {feed.bozo_exception}")
            return []

        posts: list[TrendPost] = []
        for entry in feed.entries[: self._max_items]:
            post = self._entry_to_post(entry)
            if post:
                posts.append(post)

        logger.info(f"Parsed {len(posts)} posts from GeekNews RSS")
        return posts

    def _entry_to_post(self, entry: dict) -> TrendPost | None:
        """Convert a feedparser entry to TrendPost."""
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            return None

        # Extract external_id from link (e.g., https://news.hada.io/topic?id=12345 → 12345)
        external_id = self._extract_id(link)
        if not external_id:
            external_id = link  # fallback to full URL

        # Parse published date
        published_at = None
        parsed_time = entry.get("published_parsed")
        if parsed_time:
            try:
                published_at = datetime(*parsed_time[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                pass

        # GeekNews RSS doesn't include score/comments in feed
        # These could be enriched later via page scraping if needed
        return TrendPost(
            source="GEEKNEWS",
            external_id=external_id,
            title=title,
            url=link,
            score=0,
            comment_count=0,
            published_at=published_at,
        )

    @staticmethod
    def _extract_id(url: str) -> str | None:
        """Extract topic ID from GeekNews URL."""
        # https://news.hada.io/topic?id=12345
        if "id=" in url:
            try:
                return url.split("id=")[1].split("&")[0]
            except IndexError:
                pass
        return None
