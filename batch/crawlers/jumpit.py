"""Jumpit (점핏) crawler for job postings.

Jumpit is a Korean developer job platform.
Uses internal JSON API accessible via public page XHR endpoints.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

JUMPIT_API_BASE = "https://api.jumpit.co.kr/api"
JUMPIT_JOB_URL = "https://www.jumpit.co.kr/position/{job_id}"


class JumpitCrawler(BaseCrawler):
    """Crawler for Jumpit (점핏) job listings.

    Fetches job postings via Jumpit's internal API.
    Rate limited to 1 req/sec.
    """

    def __init__(
        self,
        job_categories: list[int] | None = None,  # 1=서버/백엔드, 2=프론트엔드
        max_pages: int = 5,
        page_size: int = 16,
    ) -> None:
        self._job_categories = job_categories if job_categories is not None else [1, 2]
        self._max_pages = max_pages
        self._page_size = page_size
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
        })

    def get_source_name(self) -> str:
        return "jumpit"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl job postings from Jumpit API.

        1. Paginate through job list API for each category
        2. Fetch detail for each job
        3. Return list of RawJobPosting
        """
        seen_ids: set[int] = set()
        job_ids: list[int] = []

        for category in self._job_categories:
            for page in range(1, self._max_pages + 1):
                jobs = self._fetch_job_list(page=page, job_category=category)
                if not jobs:
                    break

                for job in jobs:
                    job_id = job.get("id")
                    if job_id and job_id not in seen_ids:
                        seen_ids.add(job_id)
                        job_ids.append(job_id)

                time.sleep(self.get_rate_limit_delay())

        logger.info(f"Found {len(job_ids)} unique jobs from Jumpit")

        postings: list[RawJobPosting] = []
        for job_id in job_ids:
            posting = self._detail_to_posting(job_id)
            if posting:
                postings.append(posting)
            time.sleep(self.get_rate_limit_delay())

        logger.info(f"Successfully fetched {len(postings)} job details from Jumpit")
        return postings

    def _fetch_job_list(self, page: int = 1, job_category: int = 1) -> list[dict]:
        """Fetch job listing page from Jumpit API."""
        try:
            resp = self._session.get(
                f"{JUMPIT_API_BASE}/positions",
                params={
                    "jobCategory": job_category,
                    "page": page,
                    "sort": "rsp_rate",
                },
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_job_list(page, job_category)

            if resp.status_code != 200:
                logger.error(f"Jumpit list API error: {resp.status_code}")
                return []

            data = resp.json()
            result = data.get("result", {})
            return result.get("positions", [])

        except requests.RequestException as e:
            logger.error(f"Jumpit list request failed: {e}")
            return []

    def _fetch_job_detail(self, job_id: int) -> dict[str, Any] | None:
        """Fetch job detail from Jumpit API."""
        try:
            resp = self._session.get(
                f"{JUMPIT_API_BASE}/position/{job_id}",
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_job_detail(job_id)

            if resp.status_code != 200:
                logger.warning(f"Jumpit detail API error for {job_id}: {resp.status_code}")
                return None

            return resp.json()

        except requests.RequestException as e:
            logger.error(f"Jumpit detail request failed for {job_id}: {e}")
            return None

    def _detail_to_posting(self, job_id: int) -> RawJobPosting | None:
        """Fetch detail and convert to RawJobPosting."""
        data = self._fetch_job_detail(job_id)
        if not data:
            return None

        result = data.get("result", {})
        company = result.get("company", {})

        # 구조화 필드 추출
        requirements_raw = result.get("qualifications")
        preferred_raw = result.get("preferredQualifications")
        responsibilities_raw = result.get("responsibility")
        benefits_raw = result.get("welfare") or result.get("benefits")
        hiring_process = result.get("process")
        employment_type = result.get("employmentType") or result.get("career")

        # Build description
        desc_parts = []
        if requirements_raw:
            desc_parts.append(f"자격요건: {requirements_raw}")
        if preferred_raw:
            desc_parts.append(f"우대사항: {preferred_raw}")
        if responsibilities_raw:
            desc_parts.append(f"주요업무: {responsibilities_raw}")
        if benefits_raw:
            desc_parts.append(f"복리후생: {benefits_raw}")

        description_raw = "\n\n".join(desc_parts)

        # Extract tech stacks
        tech_stacks = [ts.get("stack", "") for ts in result.get("techStacks", [])]
        tech_stack_raw = ", ".join(tech_stacks) if tech_stacks else None
        if tech_stacks:
            description_raw += f"\n\n기술스택: {', '.join(tech_stacks)}"

        # Mask personal info
        import re
        description_raw = re.sub(r"\S+@\S+", "[EMAIL]", description_raw)
        description_raw = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", description_raw)

        return RawJobPosting(
            title=result.get("title", ""),
            company_name=company.get("name", ""),
            description_raw=description_raw,
            source_platform="jumpit",
            source_url=JUMPIT_JOB_URL.format(job_id=job_id),
            location=result.get("workingPlace", ""),
            tags=tech_stacks,
            requirements_raw=requirements_raw,
            preferred_raw=preferred_raw,
            responsibilities_raw=responsibilities_raw,
            tech_stack_raw=tech_stack_raw,
            benefits_raw=benefits_raw,
            hiring_process=hiring_process,
            employment_type=employment_type,
        )
