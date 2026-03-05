"""Naver Career (네이버 채용) crawler for job postings.

Naver Career API: https://recruit.navercorp.com/rcrt/loadJobList.do (AJAX JSON)
Detail page: /rcrt/view.do?annoId={id} (HTML)
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests
from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

NAVER_CAREER_API = "https://recruit.navercorp.com/rcrt/loadJobList.do"
NAVER_CAREER_DETAIL = "https://recruit.navercorp.com/rcrt/view.do"
NAVER_CAREER_LIST_PAGE = "https://recruit.navercorp.com/rcrt/list.do"
NAVER_CAREER_URL = "https://recruit.navercorp.com/rcrt/view.do?annoId={anno_id}"


class NaverCareerCrawler(BaseCrawler):
    """Crawler for Naver (네이버) career postings.

    Fetches job postings via Naver's internal AJAX API.
    Rate limited to 1 req/sec. robots.txt 준수.

    세션 초기화 필요: list.do 방문으로 XSRF-TOKEN 쿠키 획득 후
    X-XSRF-TOKEN 헤더와 함께 AJAX API 호출.
    """

    def __init__(self, max_pages: int = 5, page_size: int = 20) -> None:
        self._max_pages = max_pages
        self._page_size = page_size
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://recruit.navercorp.com/rcrt/list.do",
            "Origin": "https://recruit.navercorp.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        })

    def _init_session(self) -> None:
        """list.do 방문으로 XSRF-TOKEN 쿠키 획득 후 헤더에 세팅."""
        try:
            self._session.get(NAVER_CAREER_LIST_PAGE, timeout=10)
            xsrf_token = self._session.cookies.get("XSRF-TOKEN")
            if xsrf_token:
                self._session.headers.update({"X-XSRF-TOKEN": xsrf_token})
                logger.debug("Naver Career: XSRF-TOKEN acquired")
            else:
                logger.warning("Naver Career: XSRF-TOKEN not found in cookies")
        except requests.RequestException as e:
            logger.error("Naver Career session init failed: %s", e)

    def get_source_name(self) -> str:
        return "naver_career"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl job postings from Naver Career.

        1. AJAX API로 공고 목록 페이지네이션
        2. 각 공고의 상세 페이지 HTML 파싱
        3. 자격요건/우대사항/담당업무 구조화 추출
        """
        self._init_session()
        seen_ids: set[str] = set()
        job_items: list[dict] = []

        for page in range(self._max_pages):
            first_index = page * self._page_size
            items = self._fetch_job_list(first_index=first_index)
            if not items:
                break

            for item in items:
                anno_id = str(item.get("annoId", ""))
                if anno_id and anno_id not in seen_ids:
                    seen_ids.add(anno_id)
                    job_items.append(item)

            time.sleep(self.get_rate_limit_delay())

        logger.info("Naver Career: found %d unique jobs", len(job_items))

        postings: list[RawJobPosting] = []
        for item in job_items:
            posting = self._detail_to_posting(item)
            if posting:
                postings.append(posting)
            time.sleep(self.get_rate_limit_delay())

        logger.info("Naver Career: successfully fetched %d job details", len(postings))
        return postings

    def _fetch_job_list(self, first_index: int = 0) -> list[dict]:
        """Fetch job listing page from Naver Career AJAX API."""
        try:
            resp = self._session.post(
                NAVER_CAREER_API,
                data={
                    "firstIndex": first_index,
                    "countPerPage": self._page_size,
                    "jobType": "",
                    "sysCompanyCd": "",
                    "entTypeCd": "",
                    "searchTxt": "",
                },
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited by Naver. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_job_list(first_index)

            if resp.status_code != 200:
                logger.error("Naver Career API error: %d", resp.status_code)
                return []

            data = resp.json()
            return data.get("list", data.get("result", []))

        except requests.RequestException as e:
            logger.error("Naver Career request failed: %s", e)
            return []

    def _fetch_detail_html(self, anno_id: str) -> str | None:
        """Fetch job detail HTML page."""
        try:
            resp = self._session.get(
                NAVER_CAREER_DETAIL,
                params={"annoId": anno_id},
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_detail_html(anno_id)

            if resp.status_code != 200:
                logger.warning("Naver detail error for %s: %d", anno_id, resp.status_code)
                return None

            return resp.text

        except requests.RequestException as e:
            logger.error("Naver detail request failed for %s: %s", anno_id, e)
            return None

    def _parse_detail_sections(self, html: str) -> dict[str, str | None]:
        """Parse detail HTML to extract structured sections."""
        soup = BeautifulSoup(html, "html.parser")
        sections: dict[str, str | None] = {
            "requirements_raw": None,
            "preferred_raw": None,
            "responsibilities_raw": None,
            "tech_stack_raw": None,
            "benefits_raw": None,
            "hiring_process": None,
            "full_text": "",
        }

        # 전체 텍스트 추출 (본문 영역)
        content_area = soup.select_one(".content_detail, .cont_detail, .job_detail, article, .card_area")
        full_text = content_area.get_text(separator="\n", strip=True) if content_area else soup.get_text(separator="\n", strip=True)
        sections["full_text"] = full_text

        # 섹션 헤더로 분리
        section_patterns = {
            "requirements_raw": r"(?:자격\s*요건|자격\s*조건|필수\s*요건|지원\s*자격|Requirements?|Qualifications?)",
            "preferred_raw": r"(?:우대\s*사항|우대\s*조건|Preferred|Nice\s+to\s+have)",
            "responsibilities_raw": r"(?:담당\s*업무|주요\s*업무|하는\s*일|업무\s*내용|What\s+you.*do|Responsibilities?)",
            "benefits_raw": r"(?:복리\s*후생|혜택|근무\s*조건|Benefits?|Perks)",
            "hiring_process": r"(?:채용\s*절차|채용\s*프로세스|전형\s*절차|Hiring\s+Process)",
        }

        all_headers = "|".join(f"({p})" for p in section_patterns.values())
        splits = re.split(rf"({all_headers})", full_text, flags=re.IGNORECASE)

        current_key: str | None = None
        for chunk in splits:
            if not chunk or not chunk.strip():
                continue
            chunk_stripped = chunk.strip()
            matched_key = None
            for key, pattern in section_patterns.items():
                if re.match(pattern, chunk_stripped, re.IGNORECASE):
                    matched_key = key
                    break
            if matched_key:
                current_key = matched_key
            elif current_key:
                existing = sections[current_key] or ""
                sections[current_key] = (existing + "\n" + chunk_stripped).strip()

        return sections

    def _detail_to_posting(self, item: dict[str, Any]) -> RawJobPosting | None:
        """Fetch detail and convert to RawJobPosting."""
        anno_id = str(item.get("annoId", ""))
        if not anno_id:
            return None

        title = item.get("annoSubject", item.get("title", ""))
        if not title:
            return None

        # 상세 페이지 파싱
        html = self._fetch_detail_html(anno_id)
        sections: dict[str, str | None] = {}
        full_text = ""
        if html:
            sections = self._parse_detail_sections(html)
            full_text = sections.pop("full_text", "") or ""

        # description_raw 조립
        desc_parts: list[str] = []
        if sections.get("responsibilities_raw"):
            desc_parts.append(f"담당업무: {sections['responsibilities_raw']}")
        if sections.get("requirements_raw"):
            desc_parts.append(f"자격요건: {sections['requirements_raw']}")
        if sections.get("preferred_raw"):
            desc_parts.append(f"우대사항: {sections['preferred_raw']}")
        if sections.get("benefits_raw"):
            desc_parts.append(f"복리후생: {sections['benefits_raw']}")

        description_raw = "\n\n".join(desc_parts) if desc_parts else full_text

        # PII 마스킹
        description_raw = re.sub(r"\S+@\S+", "[EMAIL]", description_raw)
        description_raw = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", description_raw)

        # 메타데이터
        location = item.get("annoWorkPlace", item.get("location", ""))
        employment_type = item.get("entTypeCd", item.get("employmentType", ""))
        experience_level = item.get("jobType", item.get("career", ""))

        return RawJobPosting(
            title=title,
            company_name="네이버",
            description_raw=description_raw,
            source_platform="naver_career",
            source_url=NAVER_CAREER_URL.format(anno_id=anno_id),
            location=location,
            experience_level=experience_level,
            requirements_raw=sections.get("requirements_raw"),
            preferred_raw=sections.get("preferred_raw"),
            responsibilities_raw=sections.get("responsibilities_raw"),
            tech_stack_raw=sections.get("tech_stack_raw"),
            benefits_raw=sections.get("benefits_raw"),
            hiring_process=sections.get("hiring_process"),
            employment_type=employment_type,
        )
