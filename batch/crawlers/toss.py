"""Toss (비바리퍼블리카) career crawler.

Fetches job postings from the Toss public career API and enriches each
posting with structured detail from the Greenhouse boards API.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting
from crawlers.greenhouse import strip_html

logger = logging.getLogger(__name__)

TOSS_JOBS_API = "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs"
GREENHOUSE_API_BASE = "https://boards-api.greenhouse.io/v1/boards"
TOSS_BOARD_TOKEN = "toss"
TOSS_COMPANY_NAME = "비바리퍼블리카"


def _mask_pii(text: str) -> str:
    """이메일·전화번호 개인정보를 마스킹한다."""
    text = re.sub(r"\S+@\S+", "[EMAIL]", text)
    text = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", text)
    return text


def _extract_sections(content_html: str) -> dict[str, str | None]:
    """HTML 콘텐츠에서 자격요건/우대사항/담당업무/복리후생 섹션을 추출한다."""
    text = strip_html(content_html)
    sections: dict[str, str | None] = {
        "requirements_raw": None,
        "preferred_raw": None,
        "responsibilities_raw": None,
        "benefits_raw": None,
    }

    patterns = {
        "requirements_raw": r"(?:자격요건|자격\s*조건|필수\s*요건|Requirements?|Qualifications?|What\s+you['']?ll\s+need)",
        "preferred_raw": r"(?:우대\s*사항|우대\s*조건|Preferred|Nice\s+to\s+have|Bonus|Plus)",
        "responsibilities_raw": r"(?:담당\s*업무|주요\s*업무|하는\s*일|What\s+you['']?ll\s+do|Responsibilities?|Role)",
        "benefits_raw": r"(?:복리\s*후생|혜택|근무\s*조건|Benefits?|Perks|What\s+we\s+offer)",
    }

    all_headers = "|".join(f"({p})" for p in patterns.values())
    splits = re.split(rf"({all_headers})", text, flags=re.IGNORECASE)

    current_key: str | None = None
    for chunk in splits:
        if not chunk or not chunk.strip():
            continue
        chunk_stripped = chunk.strip()
        matched_key = None
        for key, pattern in patterns.items():
            if re.match(pattern, chunk_stripped, re.IGNORECASE):
                matched_key = key
                break
        if matched_key:
            current_key = matched_key
        elif current_key:
            existing = sections[current_key] or ""
            sections[current_key] = (existing + "\n" + chunk_stripped).strip()

    return sections


class TossCareerCrawler(BaseCrawler):
    """Crawler for Toss (비바리퍼블리카) career postings.

    1. Fetches job list from the Toss public API.
    2. For each job, fetches structured detail from the Greenhouse boards API.
    """

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
        })

    def get_source_name(self) -> str:
        return "toss_career"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl Toss career postings and return structured RawJobPosting list."""
        jobs = self._fetch_job_list()
        logger.info(f"Found {len(jobs)} jobs from Toss career API")

        postings: list[RawJobPosting] = []
        for job in jobs:
            posting = self._job_to_posting(job)
            if posting:
                postings.append(posting)
            time.sleep(self.get_rate_limit_delay())

        logger.info(f"Collected {len(postings)} postings from {TOSS_COMPANY_NAME}")
        return postings

    def _fetch_job_list(self) -> list[dict]:
        """Toss public API에서 전체 채용 공고 목록을 가져온다."""
        try:
            resp = self._session.get(TOSS_JOBS_API, timeout=15)
            if resp.status_code != 200:
                logger.error(f"Toss jobs API error: {resp.status_code}")
                return []
            data = resp.json()
            return data.get("success", [])
        except requests.RequestException as e:
            logger.error(f"Request failed for Toss jobs API: {e}")
            return []

    def _fetch_greenhouse_detail(self, job_id: int) -> dict[str, Any] | None:
        """Greenhouse boards API에서 Toss 공고 상세 정보를 가져온다."""
        url = f"{GREENHOUSE_API_BASE}/{TOSS_BOARD_TOKEN}/jobs/{job_id}"
        try:
            resp = self._session.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Greenhouse detail error for job {job_id}: {resp.status_code}")
                return None
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Request failed for Greenhouse detail job {job_id}: {e}")
            return None

    def _job_to_posting(self, job: dict) -> RawJobPosting | None:
        """단일 job dict를 RawJobPosting으로 변환한다."""
        job_id = job.get("id")
        if not job_id:
            return None

        title = job.get("title", "")
        absolute_url = job.get("absolute_url", "")
        location_field = job.get("location")
        location = location_field.get("name", "") if isinstance(location_field, dict) else ""

        # Greenhouse detail에서 HTML content 파싱 시도
        content_html = ""
        sections: dict[str, str | None] = {
            "requirements_raw": None,
            "preferred_raw": None,
            "responsibilities_raw": None,
            "benefits_raw": None,
        }

        detail = self._fetch_greenhouse_detail(job_id)
        if detail:
            content_html = detail.get("content", "")
            if content_html:
                sections = _extract_sections(content_html)

        description_raw = strip_html(content_html) if content_html else title
        description_raw = _mask_pii(description_raw)

        return RawJobPosting(
            title=title,
            company_name=TOSS_COMPANY_NAME,
            description_raw=description_raw,
            source_platform="toss_career",
            source_url=absolute_url,
            location=location,
            tags=[],
            requirements_raw=sections["requirements_raw"],
            preferred_raw=sections["preferred_raw"],
            responsibilities_raw=sections["responsibilities_raw"],
            benefits_raw=sections["benefits_raw"],
        )
