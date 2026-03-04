"""Tech blog crawler for major Korean tech companies.

Supports RSS feed parsing (primary) and HTML fallback.
Collects blog posts for topic trend analysis over time.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

import feedparser

logger = logging.getLogger(__name__)


@dataclass
class BlogPost:
    """Raw blog post data."""

    company_name: str
    title: str
    url: str
    published_at: datetime | None = None
    published_year: int | None = None
    content_raw: str = ""
    tags: list[str] = field(default_factory=list)


# Blog configurations: company_name → RSS URL
BLOG_CONFIGS = {
    "네이버": {
        "rss_url": "https://d2.naver.com/d2/atom",
        "blog_type": "rss",
    },
    "카카오": {
        "rss_url": "https://tech.kakao.com/feed/",
        "blog_type": "rss",
    },
    "우아한형제들": {
        "rss_url": "https://techblog.woowahan.com/feed/",
        "blog_type": "rss",
    },
    "당근": {
        "rss_url": "https://medium.com/feed/daangn",
        "blog_type": "medium",
    },
    "쿠팡": {
        "rss_url": "https://medium.com/feed/coupang-engineering",
        "blog_type": "medium",
    },
}


class TechBlogCrawler:
    """Crawler for tech blog posts via RSS feeds."""

    def __init__(
        self,
        companies: list[str] | None = None,
        max_posts_per_company: int = 100,
    ) -> None:
        self._companies = companies or list(BLOG_CONFIGS.keys())
        self._max_posts = max_posts_per_company

    def crawl(self) -> list[BlogPost]:
        """Crawl blog posts from all configured companies."""
        all_posts: list[BlogPost] = []

        for company in self._companies:
            config = BLOG_CONFIGS.get(company)
            if not config:
                logger.warning(f"No config for company: {company}")
                continue

            posts = self._fetch_rss(company, config["rss_url"])
            all_posts.extend(posts)
            logger.info(f"Fetched {len(posts)} posts from {company}")

        logger.info(f"Total: {len(all_posts)} blog posts from {len(self._companies)} companies")
        return all_posts

    def _fetch_rss(self, company_name: str, rss_url: str) -> list[BlogPost]:
        """Parse RSS feed and return blog posts."""
        try:
            feed = feedparser.parse(rss_url)
        except Exception as e:
            logger.error(f"RSS fetch failed for {company_name}: {e}")
            return []

        if feed.bozo and not feed.entries:
            logger.warning(f"RSS parse error for {company_name}: {feed.get('bozo_exception', 'unknown')}")
            return []

        posts: list[BlogPost] = []
        for entry in feed.entries[: self._max_posts]:
            post = self._entry_to_post(company_name, entry)
            if post:
                posts.append(post)

        return posts

    def _entry_to_post(self, company_name: str, entry: dict) -> BlogPost | None:
        """Convert RSS entry to BlogPost."""
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            return None

        # Parse published date
        published_at = None
        published_year = None
        parsed_time = entry.get("published_parsed")
        if parsed_time:
            try:
                published_at = datetime(*parsed_time[:6], tzinfo=timezone.utc)
                published_year = published_at.year
            except (TypeError, ValueError):
                pass

        # Extract content summary
        content_raw = ""
        if entry.get("summary"):
            content_raw = entry["summary"]
        elif entry.get("content"):
            content_raw = entry["content"][0].get("value", "")

        # Extract tags
        tags = [tag.get("term", "") for tag in entry.get("tags", []) if tag.get("term")]

        return BlogPost(
            company_name=company_name,
            title=title,
            url=link,
            published_at=published_at,
            published_year=published_year,
            content_raw=content_raw,
            tags=tags,
        )
