"""Work24 (워크넷) OpenAPI crawler for job postings.

Work24 API: https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSrch.do
공공 API (1000건/일), API 키 필요.
API 키 없으면 graceful skip.
"""

from __future__ import annotations

import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import requests

from crawlers.base import BaseCrawler, RawJobPosting

logger = logging.getLogger(__name__)

WORK24_API_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSrch.do"


class Work24Crawler(BaseCrawler):
    """Crawler for Work24 (워크넷) job listings via OpenAPI.

    API 키가 없으면 빈 리스트를 반환하고 warning 로그를 남긴다.
    occupation=024 (IT/SW), region=11 (서울).
    Rate limited to 1 req/sec. XML 응답 파싱.
    """

    def __init__(
        self,
        api_key: str | None = None,
        max_count: int = 100,
    ) -> None:
        self._api_key = api_key or os.getenv("WORK24_API_KEY", "")
        self._max_count = max_count
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/xml",
        })

    def get_source_name(self) -> str:
        return "work24"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl job postings from Work24 OpenAPI."""
        if not self._api_key:
            logger.warning("WORK24_API_KEY not set. Skipping Work24 crawler.")
            return []

        postings: list[RawJobPosting] = []
        start = 1
        page_size = min(self._max_count, 100)

        while len(postings) < self._max_count:
            items = self._fetch_jobs(start=start, display=page_size)
            if not items:
                break

            for item in items:
                posting = self._item_to_posting(item)
                if posting:
                    postings.append(posting)

            if len(items) < page_size:
                break

            start += page_size
            time.sleep(self.get_rate_limit_delay())

        logger.info("Work24: collected %d postings", len(postings))
        return postings

    def _fetch_jobs(self, start: int = 1, display: int = 100) -> list[dict[str, Any]]:
        """Fetch jobs from Work24 OpenAPI."""
        try:
            resp = self._session.get(
                WORK24_API_URL,
                params={
                    "authKey": self._api_key,
                    "callTp": "L",  # List
                    "returnType": "XML",
                    "startPage": start,
                    "display": display,
                    "occupation": "024",  # IT/SW
                    "region": "11",  # 서울
                    "sortField": "DATE",
                    "sortOrder": "DESC",
                },
                timeout=15,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited by Work24. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_jobs(start, display)

            if resp.status_code == 401:
                logger.error("Work24 API key invalid or expired")
                return []

            if resp.status_code != 200:
                logger.error("Work24 API error: %d", resp.status_code)
                return []

            return self._parse_xml_response(resp.text)

        except requests.RequestException as e:
            logger.error("Work24 request failed: %s", e)
            return []

    def _parse_xml_response(self, xml_text: str) -> list[dict[str, Any]]:
        """Parse Work24 XML response to list of dicts."""
        items: list[dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error("Work24 XML parse error: %s", e)
            return []

        for wanted in root.iter("wanted"):
            item: dict[str, Any] = {}
            item["company_name"] = self._text(wanted, "company")
            item["title"] = self._text(wanted, "title")
            item["salary"] = self._text(wanted, "sal")
            item["salary_type"] = self._text(wanted, "salTpNm")
            item["location"] = self._text(wanted, "region")
            item["employment_type"] = self._text(wanted, "holidayTpNm")
            item["experience_level"] = self._text(wanted, "career")
            item["education"] = self._text(wanted, "minEdubg")
            item["url"] = self._text(wanted, "wantedInfoUrl")
            item["posting_date"] = self._text(wanted, "regDt")
            item["expiration_date"] = self._text(wanted, "closeDt")
            item["wanted_auth_no"] = self._text(wanted, "wantedAuthNo")
            item["job_type"] = self._text(wanted, "jobsCd")

            # 상세 정보
            item["responsibilities"] = self._text(wanted, "jobCont")
            item["requirements"] = self._text(wanted, "reqCareer") or self._text(wanted, "career")
            item["preferred"] = self._text(wanted, "prefCond")
            item["benefits"] = self._text(wanted, "welfare")
            item["work_type"] = self._text(wanted, "workdayWorkhr") or self._text(wanted, "enterTpNm")

            items.append(item)

        return items

    @staticmethod
    def _text(parent: ET.Element, tag: str) -> str:
        """Safely get text of child element."""
        el = parent.find(tag)
        return (el.text or "").strip() if el is not None else ""

    def _item_to_posting(self, item: dict[str, Any]) -> RawJobPosting | None:
        """Convert parsed item to RawJobPosting."""
        title = item.get("title", "")
        company_name = item.get("company_name", "")
        if not title or not company_name:
            return None

        # 구조화 필드
        requirements_raw = item.get("requirements") or None
        preferred_raw = item.get("preferred") or None
        responsibilities_raw = item.get("responsibilities") or None
        benefits_raw = item.get("benefits") or None
        work_type = item.get("work_type") or None

        # description 조립
        desc_parts: list[str] = []
        if responsibilities_raw:
            desc_parts.append(f"담당업무: {responsibilities_raw}")
        if requirements_raw:
            desc_parts.append(f"자격요건: {requirements_raw}")
        if preferred_raw:
            desc_parts.append(f"우대사항: {preferred_raw}")
        if benefits_raw:
            desc_parts.append(f"복리후생: {benefits_raw}")
        if item.get("experience_level"):
            desc_parts.append(f"경력: {item['experience_level']}")
        if item.get("education"):
            desc_parts.append(f"학력: {item['education']}")
        if item.get("salary"):
            desc_parts.append(f"급여: {item['salary']}")

        description_raw = "\n\n".join(desc_parts) if desc_parts else title

        # PII 마스킹
        description_raw = re.sub(r"\S+@\S+", "[EMAIL]", description_raw)
        description_raw = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", description_raw)

        # 날짜 파싱
        posted_at = self._parse_date(item.get("posting_date"))

        return RawJobPosting(
            title=title,
            company_name=company_name,
            description_raw=description_raw,
            source_platform="work24",
            source_url=item.get("url", ""),
            posted_at=posted_at,
            location=item.get("location"),
            experience_level=item.get("experience_level"),
            requirements_raw=requirements_raw,
            preferred_raw=preferred_raw,
            responsibilities_raw=responsibilities_raw,
            benefits_raw=benefits_raw,
            employment_type=item.get("employment_type"),
            work_type=work_type,
        )

    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
