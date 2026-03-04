"""Base trend crawler interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrendPost:
    """Raw trend post data from news/community sources."""

    source: str  # GEEKNEWS, HN, DEVTO
    external_id: str
    title: str
    url: str
    score: int = 0
    comment_count: int = 0
    published_at: datetime | None = None


class TrendCrawler(ABC):
    """Abstract base class for trend news crawlers."""

    @abstractmethod
    def crawl(self) -> list[TrendPost]:
        """Crawl and return trend posts."""
        ...

    @abstractmethod
    def get_source_name(self) -> str:
        """Return source name (e.g., 'GEEKNEWS', 'HN')."""
        ...
