"""Dictionary-based skill matcher for extracting tech keywords from text.

Core principle: Dictionary matching is the primary method.
Tech keywords in job postings are mostly English proper nouns,
so dictionary matching is more accurate than NLP approaches.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MatchedSkill:
    """A skill matched from text."""

    skill_name: str
    category: str
    matched_text: str
    source_scope: str  # JOB_POSTING, TREND, BOTH


class SkillMatcher:
    """Dictionary-based skill matcher.

    Loads skill definitions from JSON and matches against input text.
    Longer patterns are matched first to handle compound keywords correctly.
    (e.g., "Spring Boot" is matched before "Spring")
    """

    def __init__(self, skills_path: str | Path | list[dict] | None = None) -> None:
        self._skills: list[dict] = []
        self._patterns: list[tuple[re.Pattern, dict]] = []
        if skills_path is not None:
            if isinstance(skills_path, list):
                self.load_skills_from_list(skills_path)
            else:
                self.load_skills(skills_path)

    def load_skills(self, path: str | Path) -> None:
        """Load skill definitions from JSON file."""
        with open(path, encoding="utf-8") as f:
            self._skills = json.load(f)
        self._build_patterns()

    def load_skills_from_list(self, skills: list[dict]) -> None:
        """Load skill definitions from a list of dicts."""
        self._skills = skills
        self._build_patterns()

    def _build_patterns(self) -> None:
        """Build regex patterns sorted by length (longest first)."""
        entries: list[tuple[str, dict]] = []
        for skill in self._skills:
            all_names = [skill["name"]]
            if "name_ko" in skill and skill["name_ko"]:
                all_names.append(skill["name_ko"])
            all_names.extend(skill.get("aliases", []))

            for name in all_names:
                entries.append((name, skill))

        # Sort by length descending: longer patterns first
        entries.sort(key=lambda x: len(x[0]), reverse=True)

        self._patterns = []
        for name, skill in entries:
            # Build word boundary pattern
            pattern = self._build_word_pattern(name)
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._patterns.append((compiled, skill))
            except re.error:
                continue

    def _build_word_pattern(self, name: str) -> str:
        """Build a regex pattern with word boundaries.

        For English terms: prevent matching inside other English words.
          "Java" should match in "Java와 Spring" but not inside "JavaScript".
        For Korean terms: prevent matching inside other Korean words.
          "스프링" should match standalone but not inside "스프링부트" (longer match wins).
        """
        escaped = re.escape(name)
        # For patterns containing regex (like AI compound patterns),
        # use the raw pattern
        if "\\" in name and any(c in name for c in r"+*?()[]{}|"):
            return name

        # Check if the name is primarily Korean
        is_korean = any("\uac00" <= c <= "\ud7a3" for c in name)

        if is_korean:
            # Korean: prevent matching inside longer Korean words
            return rf"(?<![가-힣]){escaped}(?![가-힣])"
        else:
            # English: prevent matching inside other English words
            # Allows Korean particles (와, 를, 은, 는 etc.) right after
            return rf"(?<![a-zA-Z]){escaped}(?![a-zA-Z])"

    def match(self, text: str, scope: str | None = None) -> list[MatchedSkill]:
        """Match skills in text.

        Args:
            text: Input text to search for skills.
            scope: Filter by source_scope. If None, match all.
                   'JOB_POSTING' or 'TREND' or 'BOTH'.

        Returns:
            List of matched skills (deduplicated by skill name).
        """
        if not text:
            return []

        seen_skills: set[str] = set()
        matched_positions: list[tuple[int, int]] = []
        results: list[MatchedSkill] = []

        for pattern, skill in self._patterns:
            skill_scope = skill.get("source_scope", "BOTH")

            # Filter by scope
            if scope:
                if scope == "JOB_POSTING" and skill_scope == "TREND":
                    continue
                if scope == "TREND" and skill_scope == "JOB_POSTING":
                    continue

            skill_name = skill["name"]
            if skill_name in seen_skills:
                continue

            for m in pattern.finditer(text):
                start, end = m.start(), m.end()

                # Check overlap with already matched positions
                if any(
                    s <= start < e or s < end <= e for s, e in matched_positions
                ):
                    continue

                seen_skills.add(skill_name)
                matched_positions.append((start, end))
                results.append(
                    MatchedSkill(
                        skill_name=skill_name,
                        category=skill.get("category", ""),
                        matched_text=m.group(),
                        source_scope=skill_scope,
                    )
                )
                break  # One match per skill is enough

        return results
