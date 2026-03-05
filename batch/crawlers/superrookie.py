"""SuperRookie (superookie.com) job posting crawler.

Crawls job postings from SuperRookie's public API, including past/closed postings.
API endpoint: GET /api/jobs/search
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

SUPERROOKIE_API_BASE = "https://www.superookie.com/api/jobs/search"
SUPERROOKIE_JOB_URL = "https://www.superookie.com/jobs/{job_id}"


class SuperRookieCrawler(BaseCrawler):
    """Crawler for SuperRookie (슈퍼루키) job listings.

    Fetches job postings via SuperRookie's public search API.
    Includes closed/ended postings for historical data collection.
    Rate limited to 1 req/sec as per crawling rules.
    """

    def __init__(
        self,
        max_pages: int = 10,
        page_size: int = 20,
    ) -> None:
        self._max_pages = max_pages
        self._page_size = page_size
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
        })

    def get_source_name(self) -> str:
        return "superrookie"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl job postings from SuperRookie API.

        1. 페이지네이션으로 공고 목록 수집
        2. 마감된 공고(is_ended=true) 포함하여 과거 공고도 수집
        3. RawJobPosting으로 변환
        4. PII 마스킹 (이메일, 전화번호)
        """
        postings: list[RawJobPosting] = []
        seen_ids: set[str] = set()

        for page in range(1, self._max_pages + 1):
            jobs = self._fetch_job_list(page=page)
            if not jobs:
                break

            for job in jobs:
                job_id = str(job.get("_id", job.get("id", "")))
                if not job_id or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                posting = self._job_to_posting(job)
                if posting:
                    postings.append(posting)

            # 마지막 페이지 체크: 결과가 page_size보다 적으면 마지막
            if len(jobs) < self._page_size:
                break

            time.sleep(self.get_rate_limit_delay())

        logger.info("SuperRookie: collected %d postings from %d pages", len(postings), min(page, self._max_pages))
        return postings

    def _fetch_job_list(self, page: int = 1) -> list[dict[str, Any]]:
        """Fetch a page of job listings from SuperRookie API."""
        try:
            resp = self._session.get(
                SUPERROOKIE_API_BASE,
                params={
                    "page": page,
                    "page_length": self._page_size,
                    "short": "false",
                },
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited by SuperRookie. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_job_list(page)

            if resp.status_code != 200:
                logger.error("SuperRookie API error: %d", resp.status_code)
                return []

            data = resp.json()
            # API 응답이 리스트 또는 dict with results key
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("results", data.get("data", data.get("jobs", [])))
            return []

        except (requests.RequestException, ConnectionError) as e:
            logger.error("SuperRookie request failed (page %d): %s", page, e)
            return []

    def _job_to_posting(self, job: dict[str, Any]) -> RawJobPosting | None:
        """Convert a SuperRookie job dict to RawJobPosting."""
        title = job.get("job_title_decoded", job.get("job_title", ""))
        company = job.get("company_name_decoded", job.get("company_name", ""))

        if not title or not company:
            return None

        # 설명 조립
        desc_parts: list[str] = []
        if job.get("job_description"):
            desc_parts.append(job["job_description"])
        if job.get("requirements"):
            desc_parts.append(f"자격요건: {job['requirements']}")
        if job.get("preferred"):
            desc_parts.append(f"우대사항: {job['preferred']}")

        # 기본 정보를 설명에 추가
        meta_parts: list[str] = []
        if job.get("job_level"):
            meta_parts.append(f"경력: {job['job_level']}")
        if job.get("city"):
            meta_parts.append(f"지역: {job['city']}")
        if job.get("is_ended"):
            meta_parts.append("상태: 마감")

        if meta_parts:
            desc_parts.append(" | ".join(meta_parts))

        # 태그/스킬
        tags: list[str] = []
        if job.get("tags"):
            tags = [t if isinstance(t, str) else t.get("name", "") for t in job["tags"]]
            tags = [t for t in tags if t]
        if job.get("skills"):
            skill_tags = [s if isinstance(s, str) else s.get("name", "") for s in job["skills"]]
            tags.extend(s for s in skill_tags if s and s not in tags)

        if tags:
            desc_parts.append(f"기술스택: {', '.join(tags)}")

        description_raw = "\n\n".join(desc_parts) if desc_parts else title

        # PII 마스킹
        description_raw = self._mask_pii(description_raw)

        # 날짜 파싱
        posted_at = self._parse_date(job.get("created_at") or job.get("start_at"))

        # 위치
        location = job.get("city", job.get("location"))

        # 경력
        experience_level = job.get("job_level")

        job_id = str(job.get("_id", job.get("id", "")))

        return RawJobPosting(
            title=title,
            company_name=company,
            description_raw=description_raw,
            source_platform="superrookie",
            source_url=SUPERROOKIE_JOB_URL.format(job_id=job_id) if job_id else "",
            posted_at=posted_at,
            location=location,
            experience_level=experience_level,
            tags=tags,
        )

    @staticmethod
    def _mask_pii(text: str) -> str:
        """이메일, 전화번호 등 개인정보 마스킹."""
        text = re.sub(r"\S+@\S+", "[EMAIL]", text)
        text = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", text)
        return text

    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        """날짜 문자열을 datetime으로 파싱."""
        if not date_str:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
