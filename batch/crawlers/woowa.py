"""Woowa Brothers (배달의민족) career crawler.

Target: https://career.woowahan.com
API: GET https://career.woowahan.com/w1/recruits?pageNumber=1&pageSize=25
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from html.parser import HTMLParser
from io import StringIO
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

WOOWA_API_BASE = "https://career.woowahan.com/w1/recruits"
WOOWA_DETAIL_URL = "https://career.woowahan.com/recruitment/{recruit_number}/detail"
COMPANY_NAME = "우아한형제들"
MAX_PAGES_SAFETY = 10


class _HTMLTextExtractor(HTMLParser):
    """Simple HTML to plain text converter."""

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


def mask_pii(text: str) -> str:
    """이메일·전화번호 등 개인정보를 마스킹한다."""
    text = re.sub(r"\S+@\S+\.\S+", "[EMAIL]", text)
    text = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", text)
    return text


class WoowaCareerCrawler(BaseCrawler):
    """우아한형제들 채용 공고 크롤러.

    career.woowahan.com REST API를 통해 모든 공개 채용 공고를 수집한다.
    """

    PAGE_SIZE = 25

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/json",
            "Referer": "https://career.woowahan.com/",
        })

    def get_source_name(self) -> str:
        return "woowa_career"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def crawl(self) -> list[RawJobPosting]:
        """전체 공고를 페이지 단위로 수집해 반환한다."""
        postings: list[RawJobPosting] = []
        page = 1

        while page <= MAX_PAGES_SAFETY:
            logger.info(f"Fetching Woowa recruits page {page}")
            result = self._fetch_page(page)
            if result is None:
                logger.error(f"Failed to fetch page {page}, stopping")
                break

            jobs = result.get("list", [])
            if not jobs:
                logger.info(f"No jobs on page {page}, pagination complete")
                break

            total_pages = result.get("totalPageNumber", 1)
            logger.info(
                f"Page {page}/{total_pages}: {len(jobs)} jobs "
                f"(total {result.get('totalSize', '?')})"
            )

            for job in jobs:
                posting = self._job_to_posting(job)
                if posting:
                    postings.append(posting)
                time.sleep(self.get_rate_limit_delay())

            if page >= total_pages:
                logger.info("Last page reached")
                break

            page += 1

        logger.info(f"Woowa crawl complete: {len(postings)} postings collected")
        return postings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, page_number: int) -> dict[str, Any] | None:
        """주어진 페이지의 공고 목록을 API에서 가져온다."""
        try:
            resp = self._session.get(
                WOOWA_API_BASE,
                params={
                    "pageNumber": page_number,
                    "pageSize": self.PAGE_SIZE,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                logger.error(f"Woowa API error on page {page_number}: {resp.status_code}")
                return None

            body = resp.json()
            if body.get("code") != "2000":
                logger.error(f"Woowa API non-2000 code: {body.get('code')} – {body.get('message')}")
                return None

            return body.get("data", {})

        except requests.RequestException as e:
            logger.error(f"Request failed for page {page_number}: {e}")
            return None

    def _job_to_posting(self, job: dict[str, Any]) -> RawJobPosting | None:
        """API 응답의 공고 항목 하나를 RawJobPosting으로 변환한다."""
        recruit_number = job.get("recruitNumber", "")
        recruit_seq = job.get("recruitSeq")
        if not recruit_number and not recruit_seq:
            logger.warning("Job entry missing both recruitNumber and recruitSeq, skipping")
            return None

        title = job.get("recruitName", "").strip()
        source_url = WOOWA_DETAIL_URL.format(recruit_number=recruit_number)

        # 공고 내용 HTML → plaintext
        content_raw = job.get("recruitContents", "") or ""
        if "<" in content_raw:
            description_text = strip_html(content_raw)
        else:
            description_text = content_raw.strip()

        description_text = mask_pii(description_text)

        # 섹션 분리
        sections = self._extract_sections(description_text)

        # 게시일 파싱
        posted_at = self._parse_date(job.get("recruitOpenDate"))

        # 경력 조건 문자열 생성
        min_yr = job.get("careerRestrictionMinYears")
        max_yr = job.get("careerRestrictionMaxYears")
        experience_level = self._build_experience_level(min_yr, max_yr)

        # keywords 태그
        raw_keywords = job.get("keywords") or []
        tags = [kw.get("keyword", kw) if isinstance(kw, dict) else str(kw) for kw in raw_keywords]

        # 고용 형태
        employment_type = job.get("employmentType") or None

        return RawJobPosting(
            title=title,
            company_name=COMPANY_NAME,
            description_raw=description_text,
            source_platform=self.get_source_name(),
            source_url=source_url,
            posted_at=posted_at,
            location="서울",
            experience_level=experience_level,
            tags=tags,
            requirements_raw=sections["requirements_raw"],
            preferred_raw=sections["preferred_raw"],
            responsibilities_raw=sections["responsibilities_raw"],
            benefits_raw=sections["benefits_raw"],
            employment_type=employment_type,
        )

    def _extract_sections(self, text: str) -> dict[str, str | None]:
        """plaintext 공고 본문에서 섹션별 내용을 분리 추출한다."""
        sections: dict[str, str | None] = {
            "requirements_raw": None,
            "preferred_raw": None,
            "responsibilities_raw": None,
            "benefits_raw": None,
        }

        patterns = {
            "requirements_raw": r"(?:자격\s*요건|자격\s*조건|필수\s*요건|Requirements?|Qualifications?)",
            "preferred_raw": r"(?:우대\s*사항|우대\s*조건|Preferred|Nice\s+to\s+have)",
            "responsibilities_raw": r"(?:담당\s*업무|주요\s*업무|하는\s*일|Responsibilities?|What\s+you['']?ll\s+do)",
            "benefits_raw": r"(?:복리\s*후생|혜택|근무\s*조건|Benefits?|Perks)",
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

    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        """'YYYY-MM-DD HH:MM:SS' 형식 문자열을 datetime으로 변환한다."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.debug(f"Could not parse date: {date_str!r}")
            return None

    @staticmethod
    def _build_experience_level(min_yr: int | None, max_yr: int | None) -> str | None:
        """경력 최소/최대 연수를 읽기 좋은 문자열로 조합한다."""
        if min_yr is None and max_yr is None:
            return None
        if min_yr == 0 and (max_yr is None or max_yr == 0):
            return "신입"
        if max_yr is not None and max_yr >= 99:
            return f"{min_yr}년 이상" if min_yr else "경력무관"
        if min_yr is not None and max_yr is not None:
            return f"{min_yr}~{max_yr}년"
        if min_yr is not None:
            return f"{min_yr}년 이상"
        return None
