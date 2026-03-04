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
