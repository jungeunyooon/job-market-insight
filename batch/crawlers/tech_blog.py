"""Tech blog crawler for major Korean tech companies.

Supports RSS feed parsing (primary) and HTML fallback.
Collects blog posts for topic trend analysis over time.
Optional full-content fetching from original page HTML.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

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
    """Crawler for tech blog posts via RSS feeds.

    fetch_full_content=True 이면 RSS에서 URL 수집 후 원문 페이지 HTML을 가져와
    본문을 추출한다. 실패 시 RSS summary로 fallback.
    """

    def __init__(
        self,
        companies: list[str] | None = None,
        max_posts_per_company: int = 100,
        fetch_full_content: bool = False,
    ) -> None:
        self._companies = companies or list(BLOG_CONFIGS.keys())
        self._max_posts = max_posts_per_company
        self._fetch_full_content = fetch_full_content
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "text/html",
        })

    def crawl(self) -> list[BlogPost]:
        """Crawl blog posts from all configured companies."""
        all_posts: list[BlogPost] = []

        for company in self._companies:
            config = BLOG_CONFIGS.get(company)
            if not config:
                logger.warning(f"No config for company: {company}")
                continue

            posts = self._fetch_rss(company, config["rss_url"])

            if self._fetch_full_content:
                posts = self._enrich_with_full_content(posts)

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

    def _enrich_with_full_content(self, posts: list[BlogPost]) -> list[BlogPost]:
        """RSS에서 수집한 포스트의 원문 페이지를 가져와 content_raw를 보강한다."""
        enriched: list[BlogPost] = []
        for post in posts:
            full_content = self._fetch_page_content(post.url)
            if full_content and len(full_content) > len(post.content_raw):
                post.content_raw = full_content
            enriched.append(post)
            time.sleep(1.0)  # rate limit 1 req/sec
        return enriched

    def _fetch_page_content(self, url: str) -> str | None:
        """원문 페이지 HTML에서 본문 텍스트를 추출한다."""
        try:
            resp = self._session.get(url, timeout=10)
            if resp.status_code != 200:
                logger.debug("Full content fetch failed for %s: %d", url, resp.status_code)
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove script, style, nav, header, footer
            for tag in soup.select("script, style, nav, header, footer, aside"):
                tag.decompose()

            # Try common article selectors
            article = (
                soup.select_one("article")
                or soup.select_one(".post-content, .entry-content, .article-content")
                or soup.select_one("main")
            )

            if article:
                text = article.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # 너무 짧으면 실패로 간주
            if len(text) < 100:
                return None

            # PII 마스킹
            text = re.sub(r"\S+@\S+", "[EMAIL]", text)

            return text

        except (requests.RequestException, Exception) as e:
            logger.debug("Full content fetch error for %s: %s", url, e)
            return None
