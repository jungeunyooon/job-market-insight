"""Greenhouse Board API crawler for job postings.

Greenhouse provides a public Board API for companies that use their ATS.
Docs: https://developers.greenhouse.io/harvest.html#introduction

Target companies: Coupang, Dunamu (use Greenhouse for job boards).
"""

from __future__ import annotations

import logging
import re
import time
from html.parser import HTMLParser
from io import StringIO
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

GREENHOUSE_API_BASE = "https://boards-api.greenhouse.io/v1/boards"

# Default board tokens for target companies
DEFAULT_BOARD_TOKENS = {
    "쿠팡": "coupang",
    "두나무": "dunamu",
}


class _HTMLTextExtractor(HTMLParser):
    """Simple HTML to text converter."""

    def __init__(self) -> None:
        super().__init__()
        self._result = StringIO()

    def handle_data(self, data: str) -> None:
        self._result.write(data)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("br", "p", "div", "li", "h1", "h2", "h3", "h4"):
            self._result.write("\n")

    def get_text(self) -> str:
        return self._result.getvalue().strip()


def strip_html(html: str) -> str:
    """Strip HTML tags and return plain text."""
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


class GreenhouseCrawler(BaseCrawler):
    """Crawler for Greenhouse Board API.

    Fetches job postings from Greenhouse board for specified companies.
    """

    def __init__(
        self,
        board_tokens: dict[str, str] | None = None,
    ) -> None:
        self._board_tokens = board_tokens or DEFAULT_BOARD_TOKENS
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
        })

    def get_source_name(self) -> str:
        return "greenhouse"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl all boards and return job postings."""
        postings: list[RawJobPosting] = []

        for company_name, token in self._board_tokens.items():
            logger.info(f"Crawling Greenhouse board: {company_name} ({token})")
            jobs = self._fetch_job_list(token)
            logger.info(f"Found {len(jobs)} jobs for {company_name}")

            for job in jobs:
                posting = self._detail_to_posting(token, company_name, job)
                if posting:
                    postings.append(posting)
                time.sleep(self.get_rate_limit_delay())

        logger.info(f"Total {len(postings)} postings from {len(self._board_tokens)} boards")
        return postings

    def _fetch_job_list(self, token: str) -> list[dict]:
        """Fetch all jobs from a Greenhouse board."""
        try:
            resp = self._session.get(
                f"{GREENHOUSE_API_BASE}/{token}/jobs",
                params={"content": "false"},
                timeout=15,
            )

            if resp.status_code != 200:
                logger.error(f"Board API error for {token}: {resp.status_code}")
                return []

            data = resp.json()
            return data.get("jobs", [])

        except requests.RequestException as e:
            logger.error(f"Request failed for board {token}: {e}")
            return []

    def _fetch_job_detail(self, token: str, job_id: int) -> dict[str, Any] | None:
        """Fetch job detail with HTML content."""
        try:
            resp = self._session.get(
                f"{GREENHOUSE_API_BASE}/{token}/jobs/{job_id}",
                timeout=15,
            )

            if resp.status_code != 200:
                logger.warning(f"Job detail error for {token}/{job_id}: {resp.status_code}")
                return None

            return resp.json()

        except requests.RequestException as e:
            logger.error(f"Request failed for {token}/{job_id}: {e}")
            return None

    def _detail_to_posting(self, token: str, company_name: str, job: dict) -> RawJobPosting | None:
        """Fetch detail and convert to RawJobPosting."""
        job_id = job.get("id")
        if not job_id:
            return None

        detail = self._fetch_job_detail(token, job_id)
        if not detail:
            return None

        content_html = detail.get("content", "")
        description_raw = strip_html(content_html)

        # Mask personal info
        description_raw = re.sub(r"\S+@\S+", "[EMAIL]", description_raw)
        description_raw = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", description_raw)

        location = job.get("location", {}).get("name", "")

        return RawJobPosting(
            title=job.get("title", ""),
            company_name=company_name,
            description_raw=description_raw,
            source_platform="greenhouse",
            source_url=job.get("absolute_url", ""),
            location=location,
            tags=[],
        )
