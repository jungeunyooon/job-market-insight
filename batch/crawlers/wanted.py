"""Wanted OpenAPI crawler for job postings.

Wanted API docs: https://openapi.wanted.jobs/
Uses the public v4 API endpoints for job listing and detail.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

WANTED_API_BASE = "https://www.wanted.co.kr/api/v4"
WANTED_JOB_URL = "https://www.wanted.co.kr/wd/{job_id}"


class WantedAPICrawler(BaseCrawler):
    """Crawler for Wanted (원티드) job listings.

    Fetches job postings via Wanted's public API.
    Rate limited to 1 req/sec as per crawling rules.
    """

    # 직군별 카테고리 ID → 서로 다른 결과 풀
    DEFAULT_TAG_TYPE_IDS = {
        "서버/백엔드": "518",
        "프론트엔드": "669",
        "풀스택": "672",
        "데이터 엔지니어": "655",
        "DevOps/인프라": "660",
        "머신러닝/AI": "1634",
        "모바일(Android)": "677",
        "모바일(iOS)": "678",
        "QA/테스트": "676",
        "보안": "671",
    }

    def __init__(
        self,
        tag_type_ids: dict[str, str] | None = None,
        page_size: int = 20,
    ) -> None:
        self._tag_type_ids = tag_type_ids or self.DEFAULT_TAG_TYPE_IDS
        self._page_size = page_size
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
        })

    def get_source_name(self) -> str:
        return "wanted"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl job postings from Wanted API.

        1. Search with each keyword → collect unique job IDs
        2. Fetch detail for each unique job
        3. Return list of RawJobPosting
        """
        seen_ids: set[int] = set()
        job_ids: list[int] = []

        # Step 1: Collect unique job IDs from all categories (exhaust all pages)
        MAX_PAGES_SAFETY = 100  # 안전장치: 최대 2000개/카테고리
        for cat_name, tag_id in self._tag_type_ids.items():
            page = 0
            cat_new = 0
            while page < MAX_PAGES_SAFETY:
                offset = page * self._page_size
                jobs = self._fetch_job_list(tag_type_id=tag_id, offset=offset)
                if not jobs:
                    break

                new_in_page = 0
                for job in jobs:
                    job_id = job.get("id")
                    if job_id and job_id not in seen_ids:
                        seen_ids.add(job_id)
                        job_ids.append(job_id)
                        new_in_page += 1
                        cat_new += 1

                # Stop if last page or no new results (API recycling)
                if len(jobs) < self._page_size or new_in_page == 0:
                    break

                page += 1
                time.sleep(self.get_rate_limit_delay())

            logger.info("category='%s' (tag=%s) pages=%d new=%d total=%d",
                        cat_name, tag_id, page + 1, cat_new, len(job_ids))

        logger.info(f"Found {len(job_ids)} unique jobs from {len(self._tag_type_ids)} categories")

        # Step 2: Fetch details for each job
        postings: list[RawJobPosting] = []
        for job_id in job_ids:
            posting = self._detail_to_posting(job_id)
            if posting:
                postings.append(posting)
            time.sleep(self.get_rate_limit_delay())

        logger.info(f"Successfully fetched {len(postings)} job details")
        return postings

    def _fetch_job_list(self, tag_type_id: str, offset: int = 0) -> list[dict]:
        """Fetch job listing page from Wanted API by category."""
        try:
            resp = self._session.get(
                f"{WANTED_API_BASE}/jobs",
                params={
                    "country": "kr",
                    "tag_type_ids": tag_type_id,
                    "locations": "all",
                    "years": "-1",
                    "limit": self._page_size,
                    "offset": offset,
                },
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_job_list(keyword, offset)

            if resp.status_code != 200:
                logger.error(f"Job list API error: {resp.status_code}")
                return []

            data = resp.json()
            return data.get("data", [])

        except requests.RequestException as e:
            logger.error(f"Request failed for tag_type_id '{tag_type_id}': {e}")
            return []

    def _fetch_job_detail(self, job_id: int) -> dict[str, Any] | None:
        """Fetch job detail from Wanted API."""
        try:
            resp = self._session.get(
                f"{WANTED_API_BASE}/jobs/{job_id}",
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_job_detail(job_id)

            if resp.status_code != 200:
                logger.warning(f"Job detail API error for {job_id}: {resp.status_code}")
                return None

            return resp.json()

        except requests.RequestException as e:
            logger.error(f"Request failed for job {job_id}: {e}")
            return None

    def _detail_to_posting(self, job_id: int) -> RawJobPosting | None:
        """Fetch detail and convert to RawJobPosting."""
        data = self._fetch_job_detail(job_id)
        if not data:
            return None

        job = data.get("job", {})
        detail = job.get("detail", {})
        company = job.get("company", {})
        address = job.get("address", {})

        # 구조화 필드 추출
        requirements_raw = detail.get("requirements")
        preferred_raw = detail.get("preferred")
        responsibilities_raw = detail.get("main_tasks")
        intro = detail.get("intro", "")
        benefits = detail.get("benefits")
        hiring_process = detail.get("hiring_process")

        # Build description from detail sections
        desc_parts = []
        if intro:
            desc_parts.append(intro)
        if responsibilities_raw:
            desc_parts.append(f"주요업무: {responsibilities_raw}")
        if requirements_raw:
            desc_parts.append(f"자격요건: {requirements_raw}")
        if preferred_raw:
            desc_parts.append(f"우대사항: {preferred_raw}")
        if benefits:
            desc_parts.append(f"복리후생: {benefits}")

        description_raw = "\n\n".join(desc_parts)

        # Extract skill tags
        skill_tags = [tag.get("title", "") for tag in job.get("skill_tags", [])]
        tech_stack_raw = ", ".join(skill_tags) if skill_tags else None
        if skill_tags:
            description_raw += f"\n\n기술스택: {', '.join(skill_tags)}"

        # Mask personal info (email, phone)
        import re
        description_raw = re.sub(r"\S+@\S+", "[EMAIL]", description_raw)
        description_raw = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", description_raw)

        return RawJobPosting(
            title=job.get("position", ""),
            company_name=company.get("name", ""),
            description_raw=description_raw,
            source_platform="wanted",
            source_url=WANTED_JOB_URL.format(job_id=job_id),
            location=address.get("full_location", job.get("location", "")),
            tags=skill_tags,
            requirements_raw=requirements_raw,
            preferred_raw=preferred_raw,
            responsibilities_raw=responsibilities_raw,
            tech_stack_raw=tech_stack_raw,
            benefits_raw=benefits,
            hiring_process=hiring_process,
        )
