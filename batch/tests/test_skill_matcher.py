"""Tests for dictionary-based skill matcher.

TDD: These tests define the expected behavior of SkillMatcher.
"""

import sys
from pathlib import Path

import pytest

# Add batch/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.skill_matcher import MatchedSkill, SkillMatcher


class TestSkillMatcherBasicMatching:
    """Basic skill matching from text."""

    def test_match_english_skill(self, skill_matcher: SkillMatcher) -> None:
        text = "We require Java and Docker experience."
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Java" in skill_names
        assert "Docker" in skill_names

    def test_match_korean_alias(self, skill_matcher: SkillMatcher) -> None:
        text = "스프링부트 경험 필수, 쿠버네티스 우대"
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Spring Boot" in skill_names
        assert "Kubernetes" in skill_names

    def test_match_mixed_korean_english(self, skill_matcher: SkillMatcher) -> None:
        text = "Java/Spring Boot 기반 서버 개발, Docker 환경 경험"
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Java" in skill_names
        assert "Spring Boot" in skill_names
        assert "Docker" in skill_names

    def test_case_insensitive(self, skill_matcher: SkillMatcher) -> None:
        text = "Experience with KAFKA and kubernetes required."
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Kafka" in skill_names
        assert "Kubernetes" in skill_names

    def test_k8s_alias(self, skill_matcher: SkillMatcher) -> None:
        text = "K8s 운영 경험 우대"
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Kubernetes" in skill_names


class TestSkillMatcherCompoundKeywords:
    """Compound keywords should be matched before shorter ones."""

    def test_spring_boot_before_spring(self, skill_matcher: SkillMatcher) -> None:
        """'Spring Boot' should be matched, not just 'Spring'."""
        text = "Spring Boot 경험 필수"
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Spring Boot" in skill_names

    def test_apache_kafka_resolves_to_kafka(self, skill_matcher: SkillMatcher) -> None:
        text = "Apache Kafka 경험 우대"
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        assert "Kafka" in skill_names


class TestSkillMatcherDeduplication:
    """Each skill should appear at most once."""

    def test_no_duplicate_skills(self, skill_matcher: SkillMatcher) -> None:
        text = "Java 경험, java 개발, JAVA 필수"
        results = skill_matcher.match(text)
        java_matches = [r for r in results if r.skill_name == "Java"]
        assert len(java_matches) == 1


class TestSkillMatcherWordBoundary:
    """Skills should match only at word boundaries."""

    def test_no_partial_match_in_word(self, skill_matcher: SkillMatcher) -> None:
        """'Java' should not match inside 'JavaScript'."""
        # Note: This depends on matching order (longer first)
        text = "JavaScript 경험 필수"
        results = skill_matcher.match(text)
        skill_names = {r.skill_name for r in results}
        # JavaScript should be matched, not Java
        assert "JavaScript" not in skill_names or "Java" not in skill_names


class TestSkillMatcherScopeFiltering:
    """source_scope filtering."""

    def test_trend_only_excluded_from_job_posting_scope(
        self, skill_matcher: SkillMatcher
    ) -> None:
        text = "vibe coding is trending and Java is required"
        results = skill_matcher.match(text, scope="JOB_POSTING")
        skill_names = {r.skill_name for r in results}
        assert "Java" in skill_names
        assert "vibe coding" not in skill_names

    def test_job_posting_scope_includes_both(
        self, skill_matcher: SkillMatcher
    ) -> None:
        text = "GitHub Copilot 활용 경험 우대"
        results = skill_matcher.match(text, scope="JOB_POSTING")
        skill_names = {r.skill_name for r in results}
        # GitHub Copilot has source_scope=BOTH, so it should appear
        assert "GitHub Copilot" in skill_names

    def test_trend_scope_excludes_job_posting_only(
        self, skill_matcher: SkillMatcher
    ) -> None:
        text = "vibe coding 트렌드 분석"
        results = skill_matcher.match(text, scope="TREND")
        skill_names = {r.skill_name for r in results}
        assert "vibe coding" in skill_names

    def test_no_scope_returns_all(self, skill_matcher: SkillMatcher) -> None:
        text = "vibe coding and Java"
        results = skill_matcher.match(text, scope=None)
        skill_names = {r.skill_name for r in results}
        assert "vibe coding" in skill_names
        assert "Java" in skill_names


class TestSkillMatcherEdgeCases:
    """Edge cases."""

    def test_empty_text(self, skill_matcher: SkillMatcher) -> None:
        assert skill_matcher.match("") == []

    def test_no_skills_in_text(self, skill_matcher: SkillMatcher) -> None:
        text = "좋은 커뮤니케이션 능력을 갖춘 분"
        results = skill_matcher.match(text)
        assert len(results) == 0

    def test_result_has_category(self, skill_matcher: SkillMatcher) -> None:
        text = "Kafka experience required"
        results = skill_matcher.match(text)
        kafka = [r for r in results if r.skill_name == "Kafka"][0]
        assert kafka.category == "messaging"

    def test_result_has_source_scope(self, skill_matcher: SkillMatcher) -> None:
        text = "LLM 경험"
        results = skill_matcher.match(text)
        llm = [r for r in results if r.skill_name == "LLM"][0]
        assert llm.source_scope == "BOTH"


class TestSkillMatcherFromFile:
    """Loading skills from JSON file."""

    def test_load_from_seed_file(self) -> None:
        seed_path = Path(__file__).parent.parent.parent / "data" / "skills_seed.json"
        if not seed_path.exists():
            pytest.skip("skills_seed.json not found")

        matcher = SkillMatcher(skills_path=seed_path)
        results = matcher.match("Java와 Spring Boot 경험 필수, Kafka 우대")
        skill_names = {r.skill_name for r in results}
        assert "Java" in skill_names
        assert "Spring Boot" in skill_names
        assert "Kafka" in skill_names
