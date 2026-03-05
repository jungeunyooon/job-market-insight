"""Base crawler interface for all job posting crawlers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawJobPosting:
    """Raw job posting data from crawler before normalization."""

    title: str
    company_name: str
    description_raw: str
    source_platform: str
    source_url: str
    posted_at: datetime | None = None
    location: str | None = None
    experience_level: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    tags: list[str] = field(default_factory=list)

    # 구조화 필드 — 채용공고 섹션별 원문 보존
    requirements_raw: str | None = None       # 자격요건
    preferred_raw: str | None = None          # 우대사항
    responsibilities_raw: str | None = None   # 담당업무 / 하는 일
    tech_stack_raw: str | None = None         # 기술스택 (태그/텍스트)
    benefits_raw: str | None = None           # 복리후생 / 근무조건

    # 추가 메타데이터
    company_size: str | None = None           # 회사 규모 (예: "50-100명")
    team_info: str | None = None              # 팀 소개
    hiring_process: str | None = None         # 채용 프로세스
    employment_type: str | None = None        # 고용 형태 (정규직/계약직/인턴)
    work_type: str | None = None              # 근무 형태 (원격/하이브리드/출근)


class BaseCrawler(ABC):
    """Abstract base class for all crawlers."""

    @abstractmethod
    def crawl(self) -> list[RawJobPosting]:
        """Crawl and return raw job postings."""
        ...

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this crawler's source (e.g., 'wanted', 'jumpit')."""
        ...

    def get_rate_limit_delay(self) -> float:
        """Rate limit delay in seconds between requests. Default: 1.0s per domain."""
        return 1.0
