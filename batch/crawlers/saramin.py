"""Saramin (사람인) OpenAPI crawler for job postings.

Saramin OpenAPI: https://oapi.saramin.co.kr/job-search
공식 API (500건/일), API 키 필요.
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

SARAMIN_API_URL = "https://oapi.saramin.co.kr/job-search"


class SaraminAPICrawler(BaseCrawler):
    """Crawler for Saramin (사람인) job listings via OpenAPI.

    API 키가 없으면 빈 리스트를 반환하고 warning 로그를 남긴다.
    Rate limited to 1 req/sec. XML 응답 파싱.
    """

    def __init__(
        self,
        api_key: str | None = None,
        keywords: list[str] | None = None,
        max_count: int = 100,
    ) -> None:
        self._api_key = api_key or os.getenv("SARAMIN_API_KEY", "")
        self._keywords = keywords or ["백엔드", "서버개발", "Backend"]
        self._max_count = max_count
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "DevPulse-Bot/1.0 (+https://github.com/jungeunyooon/job-market-insight)",
            "Accept": "application/xml",
        })

    def get_source_name(self) -> str:
        return "saramin"

    def get_rate_limit_delay(self) -> float:
        return 1.0

    def crawl(self) -> list[RawJobPosting]:
        """Crawl job postings from Saramin OpenAPI."""
        if not self._api_key:
            logger.warning("SARAMIN_API_KEY not set. Skipping Saramin crawler.")
            return []

        seen_urls: set[str] = set()
        postings: list[RawJobPosting] = []

        for keyword in self._keywords:
            items = self._fetch_jobs(keyword)
            for item in items:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    posting = self._item_to_posting(item)
                    if posting:
                        postings.append(posting)

            time.sleep(self.get_rate_limit_delay())

        logger.info("Saramin: collected %d postings from %d keywords", len(postings), len(self._keywords))
        return postings

    def _fetch_jobs(self, keyword: str) -> list[dict[str, Any]]:
        """Fetch jobs from Saramin OpenAPI for a keyword."""
        try:
            resp = self._session.get(
                SARAMIN_API_URL,
                params={
                    "access-key": self._api_key,
                    "keywords": keyword,
                    "count": self._max_count,
                    "start": 0,
                    "job_type": "1",  # 정규직
                    "sort": "D",  # 최신순
                    "fields": "posting-date+expiration-date+keyword-code+count",
                },
                timeout=15,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited by Saramin. Waiting 5 seconds...")
                time.sleep(5)
                return self._fetch_jobs(keyword)

            if resp.status_code == 401:
                logger.error("Saramin API key invalid or expired")
                return []

            if resp.status_code != 200:
                logger.error("Saramin API error: %d", resp.status_code)
                return []

            return self._parse_xml_response(resp.text)

        except requests.RequestException as e:
            logger.error("Saramin request failed for keyword '%s': %s", keyword, e)
            return []

    def _parse_xml_response(self, xml_text: str) -> list[dict[str, Any]]:
        """Parse Saramin XML response to list of dicts."""
        items: list[dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error("Saramin XML parse error: %s", e)
            return []

        for job in root.iter("job"):
            item: dict[str, Any] = {}

            # 기본 정보
            pos = job.find("position")
            if pos is not None:
                item["title"] = self._text(pos, "title")
                industry = pos.find("industry")
                item["industry"] = self._text(industry, "name") if industry is not None else ""
                location = pos.find("location")
                item["location"] = self._text(location, "name") if location is not None else ""
                job_type = pos.find("job-type")
                item["employment_type"] = self._text(job_type, "name") if job_type is not None else ""
                experience = pos.find("experience-level")
                item["experience_level"] = self._text(experience, "name") if experience is not None else ""
                req_edu = pos.find("required-education-level")
                item["education"] = self._text(req_edu, "name") if req_edu is not None else ""

            company = job.find("company")
            if company is not None:
                detail = company.find("detail")
                item["company_name"] = self._text(detail, "name") if detail is not None else ""
                href = detail.find("href") if detail is not None else None
                item["company_url"] = href.text if href is not None and href.text else ""

            item["url"] = job.get("url", "")
            item["posting_date"] = self._text(job, "posting-date")
            item["expiration_date"] = self._text(job, "expiration-date")

            # salary
            salary = job.find("salary")
            if salary is not None:
                item["salary"] = self._text(salary, "name")

            # keyword
            keyword_el = job.find("keyword")
            if keyword_el is not None and keyword_el.text:
                item["keywords"] = keyword_el.text

            items.append(item)

        return items

    @staticmethod
    def _text(parent: ET.Element | None, tag: str) -> str:
        """Safely get text of child element."""
        if parent is None:
            return ""
        el = parent.find(tag)
        return (el.text or "").strip() if el is not None else ""

    def _item_to_posting(self, item: dict[str, Any]) -> RawJobPosting | None:
        """Convert parsed item to RawJobPosting."""
        title = item.get("title", "")
        company_name = item.get("company_name", "")
        if not title or not company_name:
            return None

        # description 조립
        desc_parts: list[str] = []
        if item.get("industry"):
            desc_parts.append(f"산업: {item['industry']}")
        if item.get("experience_level"):
            desc_parts.append(f"경력: {item['experience_level']}")
        if item.get("education"):
            desc_parts.append(f"학력: {item['education']}")
        if item.get("salary"):
            desc_parts.append(f"급여: {item['salary']}")
        if item.get("keywords"):
            desc_parts.append(f"기술스택: {item['keywords']}")

        description_raw = "\n\n".join(desc_parts) if desc_parts else title

        # PII 마스킹
        description_raw = re.sub(r"\S+@\S+", "[EMAIL]", description_raw)
        description_raw = re.sub(r"\d{2,3}-\d{3,4}-\d{4}", "[PHONE]", description_raw)

        # 기술스택 추출
        tech_stack_raw = item.get("keywords")
        tags = [k.strip() for k in tech_stack_raw.split(",")] if tech_stack_raw else []

        # 날짜 파싱
        posted_at = self._parse_date(item.get("posting_date"))

        return RawJobPosting(
            title=title,
            company_name=company_name,
            description_raw=description_raw,
            source_platform="saramin",
            source_url=item.get("url", ""),
            posted_at=posted_at,
            location=item.get("location"),
            experience_level=item.get("experience_level"),
            tags=tags,
            tech_stack_raw=tech_stack_raw,
            employment_type=item.get("employment_type"),
        )

    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
