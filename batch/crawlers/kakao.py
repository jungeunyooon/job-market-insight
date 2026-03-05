"""Kakao Career API crawler for job postings.

Kakao provides a public JSON API for their careers site.
API endpoint: https://careers.kakao.com/public/api/job-list
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

KAKAO_JOB_LIST_URL = "https://careers.kakao.com/public/api/job-list"
KAKAO_JOB_URL_TEMPLATE = "https://careers.kakao.com/jobs/{real_id}"


class KakaoCareerCrawler(BaseCrawler):
    """Crawler for Kakao career postings via public JSON API."""

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
            "Referer": "https://careers.kakao.com/",
        })

    def get_source_name(self) -> str:
        return "kakao_career"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Fetch Kakao job list and convert each to RawJobPosting."""
        logger.info("Crawling Kakao Career API")
        jobs = self._fetch_job_list()
        logger.info(f"Found {len(jobs)} jobs from Kakao Career")

        postings: list[RawJobPosting] = []
        for job in jobs:
            posting = self._job_to_posting(job)
            if posting:
                postings.append(posting)
            time.sleep(self.get_rate_limit_delay())

        logger.info(f"Total {len(postings)} postings from Kakao Career")
        return postings

    def _fetch_job_list(self) -> list[dict[str, Any]]:
        """Fetch the job list from Kakao Career API."""
        try:
            resp = self._session.get(KAKAO_JOB_LIST_URL, timeout=15)

            if resp.status_code != 200:
                logger.error(f"Kakao Career API error: {resp.status_code}")
                return []

            data = resp.json()
            return data.get("jobList", [])

        except requests.RequestException as e:
            logger.error(f"Request failed for Kakao Career API: {e}")
            return []

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string from API (YYYY-MM-DD or ISO format)."""
        if not date_str:
            return None
        candidates = [
            ("%Y-%m-%d", 10),
            ("%Y-%m-%dT%H:%M:%S", 19),
            ("%Y.%m.%d", 10),
        ]
        for fmt, length in candidates:
            try:
                return datetime.strptime(date_str[:length], fmt)
            except ValueError:
                continue
        logger.debug(f"Could not parse date: {date_str!r}")
        return None

    def _mask_pii(self, text: str) -> str:
        """Mask personally identifiable information."""
        text = re.sub(r"\S+@\S+", "[EMAIL]", text)
        text = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", text)
        return text

    def _build_description_raw(self, job: dict[str, Any]) -> str:
        """Combine introduction, workContentDesc, and qualification into description_raw."""
        parts: list[str] = []

        introduction = (job.get("introduction") or "").strip()
        if introduction:
            parts.append(introduction)

        work_content = (job.get("workContentDesc") or "").strip()
        if work_content:
            parts.append(work_content)

        qualification = (job.get("qualification") or "").strip()
        if qualification:
            parts.append(qualification)

        process_desc = (job.get("jobOfferProcessDesc") or "").strip()
        if process_desc:
            parts.append(process_desc)

        return "\n\n".join(parts)

    def _job_to_posting(self, job: dict[str, Any]) -> RawJobPosting | None:
        """Convert a Kakao API job dict to RawJobPosting."""
        real_id = job.get("realId")
        if not real_id:
            logger.warning("Skipping job with no realId")
            return None

        title = (job.get("jobOfferTitle") or "").strip()
        if not title:
            logger.warning(f"Skipping job {real_id} with empty title")
            return None

        source_url = KAKAO_JOB_URL_TEMPLATE.format(real_id=real_id)

        description_raw = self._mask_pii(self._build_description_raw(job))
        responsibilities_raw = self._mask_pii((job.get("workContentDesc") or "").strip()) or None
        requirements_raw = self._mask_pii((job.get("qualification") or "").strip()) or None

        # skillSetList is a list of skill tag strings
        skill_set = job.get("skillSetList") or []
        tags = [str(s).strip() for s in skill_set if str(s).strip()]

        posted_at = self._parse_date(job.get("regDate"))
        location = (job.get("locationName") or "").strip() or None
        employment_type = (job.get("employeeTypeName") or "").strip() or None

        logger.debug(f"Parsed posting: {real_id} — {title}")

        return RawJobPosting(
            title=title,
            company_name="카카오",
            description_raw=description_raw,
            source_platform="kakao_career",
            source_url=source_url,
            posted_at=posted_at,
            location=location,
            tags=tags,
            responsibilities_raw=responsibilities_raw,
            requirements_raw=requirements_raw,
            employment_type=employment_type,
        )
