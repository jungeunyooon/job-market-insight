"""HackerNews Firebase API crawler for developer trend tracking.

Uses the official HN Firebase REST API:
  https://hacker-news.firebaseio.com/v0/
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import requests

from crawlers.trend.base import TrendCrawler, TrendPost

logger = logging.getLogger(__name__)

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"
HN_ITEM_URL = "https://news.ycombinator.com/item?id={id}"

_REQUEST_TIMEOUT = 10  # seconds


class HackerNewsCrawler(TrendCrawler):
    """Crawler for HackerNews top stories via Firebase API."""

    def __init__(
        self,
        base_url: str = HN_BASE_URL,
        max_items: int = 30,
        rate_limit_delay: float = 0.1,
    ) -> None:
        self._base_url = base_url
        self._max_items = max_items
        self._rate_limit_delay = rate_limit_delay

    def get_source_name(self) -> str:
        return "HN"

    def crawl(self) -> list[TrendPost]:
        """Fetch top HN stories and return as TrendPost list."""
        logger.info("Fetching HackerNews top stories")
        story_ids = self._fetch_top_story_ids()
        if not story_ids:
            return []

        posts: list[TrendPost] = []
        for story_id in story_ids[: self._max_items]:
            item = self._fetch_item(story_id)
            if item is None:
                continue
            post = self._item_to_post(item)
            if post:
                posts.append(post)
            time.sleep(self._rate_limit_delay)

        logger.info(f"Collected {len(posts)} posts from HackerNews")
        return posts

    def _fetch_top_story_ids(self) -> list[int]:
        """Fetch list of top story IDs from HN API."""
        url = f"{self._base_url}/topstories.json"
        try:
            resp = requests.get(url, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error(f"Failed to fetch HN top stories: {exc}")
            return []

    def _fetch_item(self, item_id: int) -> dict | None:
        """Fetch a single HN item by ID."""
        url = f"{self._base_url}/item/{item_id}.json"
        try:
            resp = requests.get(url, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning(f"Failed to fetch HN item {item_id}: {exc}")
            return None

    def _item_to_post(self, item: dict) -> TrendPost | None:
        """Convert a HN item dict to TrendPost.

        Only 'story' type items with a non-empty title are included.
        Items without a url (e.g. Ask HN) fall back to the HN item page URL.
        """
        if item.get("type") != "story":
            return None

        title = (item.get("title") or "").strip()
        if not title:
            return None

        item_id = item["id"]
        url = (item.get("url") or "").strip() or HN_ITEM_URL.format(id=item_id)

        score = item.get("score", 0) or 0
        comment_count = item.get("descendants", 0) or 0

        published_at: datetime | None = None
        unix_time = item.get("time")
        if unix_time:
            try:
                published_at = datetime.fromtimestamp(unix_time, tz=timezone.utc)
            except (TypeError, ValueError, OSError):
                pass

        return TrendPost(
            source="HN",
            external_id=str(item_id),
            title=title,
            url=url,
            score=score,
            comment_count=comment_count,
            published_at=published_at,
        )
