"""Job title and company name normalizer."""

from __future__ import annotations

import json
import re
from pathlib import Path


class PositionNormalizer:
    """Normalize Korean/English job titles to standard position types."""

    DEFAULT_MAPPINGS: dict[str, list[str]] = {
        "BACKEND": [
            "백엔드",
            "서버 개발자",
            "서버개발자",
            "Backend Engineer",
            "Backend Developer",
            "Server Developer",
            "Server Engineer",
            "BE Developer",
            "Platform Engineer",
        ],
        "FRONTEND": [
            "프론트엔드",
            "프론트엔드 개발자",
            "Frontend Engineer",
            "Frontend Developer",
            "FE Developer",
            "UI Developer",
            "UI Engineer",
        ],
        "FULLSTACK": [
            "풀스택",
            "풀스택 개발자",
            "Full-stack",
            "Fullstack",
            "Full Stack",
            "Fullstack Developer",
            "Full Stack Engineer",
        ],
        "PRODUCT": [
            "프로덕트 엔지니어",
            "Product Engineer",
        ],
        "FDE": [
            "FDE",
            "Forward Deployed Engineer",
            "Solutions Engineer",
            "Technical Consultant",
        ],
    }

    def __init__(self, aliases_path: str | Path | None = None) -> None:
        self._mappings: dict[str, list[str]] = {}
        if aliases_path:
            self.load_aliases(aliases_path)
        else:
            self._mappings = self.DEFAULT_MAPPINGS.copy()
        self._build_patterns()

    def load_aliases(self, path: str | Path) -> None:
        """Load position aliases from JSON file."""
        with open(path, encoding="utf-8") as f:
            self._mappings = json.load(f)
        self._build_patterns()

    def _build_patterns(self) -> None:
        """Build compiled regex patterns for each position type."""
        self._patterns: list[tuple[re.Pattern, str]] = []
        for position_type, aliases in self._mappings.items():
            for alias in aliases:
                escaped = re.escape(alias)
                pattern = re.compile(escaped, re.IGNORECASE)
                self._patterns.append((pattern, position_type))

    def normalize(self, title: str) -> str | None:
        """Normalize a job title to a standard position type.

        Returns:
            Position type string (BACKEND, PRODUCT, FDE) or None if no match.
        """
        if not title:
            return None

        for pattern, position_type in self._patterns:
            if pattern.search(title):
                return position_type

        return None


class CompanyNormalizer:
    """Normalize company names using aliases."""

    def __init__(self, companies: list[dict] | None = None) -> None:
        self._companies: dict[str, dict] = {}
        self._alias_map: dict[str, str] = {}
        if companies:
            self.load_companies(companies)

    def load_companies(self, companies: list[dict]) -> None:
        """Load company data with aliases."""
        self._companies = {}
        self._alias_map = {}
        for company in companies:
            name = company["name"]
            self._companies[name.lower()] = company

            # Map all aliases to the canonical name
            for alias in company.get("aliases", []):
                self._alias_map[alias.lower()] = name
            if "name_en" in company:
                self._alias_map[company["name_en"].lower()] = name

    def normalize(self, raw_name: str) -> str | None:
        """Normalize a company name to canonical form.

        Returns:
            Canonical company name, or None if not found.
        """
        if not raw_name:
            return None

        lower = raw_name.strip().lower()

        # Direct match
        if lower in self._companies:
            return self._companies[lower]["name"]

        # Alias match
        if lower in self._alias_map:
            return self._alias_map[lower]

        return None
