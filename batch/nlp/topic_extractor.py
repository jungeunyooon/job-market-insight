"""Topic extractor for tech blog posts.

Uses SkillMatcher to extract technology topics from blog titles and content.
Phase 2: Dictionary-based extraction (title + tags).
Phase 3: LLM-based extraction for deeper analysis.
"""

from __future__ import annotations

from dataclasses import dataclass

from nlp.skill_matcher import SkillMatcher


@dataclass
class ExtractedTopic:
    """Topic extracted from a blog post."""

    skill_name: str
    category: str
    source: str  # 'title', 'tags', 'content'


class TopicExtractor:
    """Extract technology topics from blog posts using SkillMatcher."""

    def __init__(self, matcher: SkillMatcher) -> None:
        self._matcher = matcher

    def extract_from_title(self, title: str) -> list[ExtractedTopic]:
        """Extract topics from blog post title."""
        matches = self._matcher.match(title)
        return [
            ExtractedTopic(skill_name=m.skill_name, category=m.category, source="title")
            for m in matches
        ]

    def extract_from_tags(self, tags: list[str]) -> list[ExtractedTopic]:
        """Extract topics from blog post tags/categories."""
        seen = set()
        topics = []
        for tag in tags:
            matches = self._matcher.match(tag)
            for m in matches:
                if m.skill_name not in seen:
                    seen.add(m.skill_name)
                    topics.append(
                        ExtractedTopic(skill_name=m.skill_name, category=m.category, source="tags")
                    )
        return topics

    def extract_all(self, title: str, tags: list[str] | None = None, content: str | None = None) -> list[ExtractedTopic]:
        """Extract all unique topics from title, tags, and optional content.

        Deduplicates by skill_name, keeping the first source found.
        Priority: title > tags > content.
        """
        seen: set[str] = set()
        topics: list[ExtractedTopic] = []

        # 1. Title (highest priority)
        for t in self.extract_from_title(title):
            if t.skill_name not in seen:
                seen.add(t.skill_name)
                topics.append(t)

        # 2. Tags
        if tags:
            for t in self.extract_from_tags(tags):
                if t.skill_name not in seen:
                    seen.add(t.skill_name)
                    topics.append(t)

        # 3. Content (lower priority, more noise)
        if content:
            content_matches = self._matcher.match(content)
            for m in content_matches:
                if m.skill_name not in seen:
                    seen.add(m.skill_name)
                    topics.append(
                        ExtractedTopic(skill_name=m.skill_name, category=m.category, source="content")
                    )

        return topics
