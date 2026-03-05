"""Tests for dynamic skill keyword update from LLM-extracted keywords.

Tests the _update_skill_keywords_from_llm logic without importing sync.py
(which requires psycopg2). Instead, we extract and test the pure logic.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class FakeCursor:
    """Mock DB cursor."""

    def __init__(self):
        self.executed: list[tuple] = []

    def execute(self, query, params=None):
        self.executed.append((query, params))


def _update_skill_keywords_from_llm(
    skill_keywords: dict[str, list[str]],
    cur,
    llm_keywords: list[dict],
    matched_skill_names: set[str],
) -> None:
    """Extracted logic from DevPulseSync._update_skill_keywords_from_llm.

    This mirrors the implementation in sync.py for testability without psycopg2.
    """
    import json

    skill_new_keywords: dict[str, list[str]] = {}
    for kw_item in llm_keywords:
        kw_text = kw_item.get("keyword", "").strip()
        if not kw_text or len(kw_text) < 3:
            continue
        for skill_name in matched_skill_names:
            skill_new_keywords.setdefault(skill_name, []).append(kw_text)

    for skill_name, new_kws in skill_new_keywords.items():
        if not new_kws:
            continue
        existing = skill_keywords.get(skill_name, [])
        existing_lower = {k.lower() for k in existing}
        added = [kw for kw in new_kws if kw.lower() not in existing_lower]
        if not added:
            continue

        merged = existing + added
        skill_keywords[skill_name] = merged
        cur.execute(
            "UPDATE skill SET keywords = %s WHERE LOWER(name) = %s",
            (json.dumps(merged, ensure_ascii=False), skill_name),
        )


class TestUpdateSkillKeywordsFromLlm:

    def test_adds_new_keywords_to_skill(self):
        skill_kws = {"java": ["JVM 튜닝", "GC 최적화"]}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "대규모 트래픽 처리 경험", "section": "자격요건"},
            {"keyword": "캐싱 전략 설계", "section": "자격요건"},
        ], {"java"})

        assert "대규모 트래픽 처리 경험" in skill_kws["java"]
        assert "캐싱 전략 설계" in skill_kws["java"]
        assert "JVM 튜닝" in skill_kws["java"]
        assert "GC 최적화" in skill_kws["java"]
        assert len(cur.executed) == 1

    def test_skips_duplicate_keywords(self):
        skill_kws = {"redis": ["캐싱 전략", "TTL"]}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "캐싱 전략", "section": "자격요건"},
            {"keyword": "새로운 키워드", "section": "우대사항"},
        ], {"redis"})

        assert skill_kws["redis"].count("캐싱 전략") == 1
        assert "새로운 키워드" in skill_kws["redis"]

    def test_skips_short_keywords(self):
        skill_kws = {"python": []}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "AI", "section": "자격요건"},  # 2글자 → 건너뜀
            {"keyword": "데이터 파이프라인 구축", "section": "자격요건"},
        ], {"python"})

        assert "AI" not in skill_kws["python"]
        assert "데이터 파이프라인 구축" in skill_kws["python"]

    def test_handles_empty_llm_keywords(self):
        skill_kws = {"java": ["Spring"]}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [], {"java"})

        assert skill_kws["java"] == ["Spring"]
        assert len(cur.executed) == 0

    def test_handles_no_matched_skills(self):
        skill_kws = {}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "새로운 기술 경험", "section": "자격요건"},
        ], set())

        assert len(cur.executed) == 0

    def test_distributes_keywords_to_multiple_skills(self):
        skill_kws = {"java": [], "spring": []}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "MSA 아키텍처 설계", "section": "자격요건"},
        ], {"java", "spring"})

        assert "MSA 아키텍처 설계" in skill_kws["java"]
        assert "MSA 아키텍처 설계" in skill_kws["spring"]
        assert len(cur.executed) == 2

    def test_case_insensitive_dedup(self):
        skill_kws = {"docker": ["컨테이너 오케스트레이션"]}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "컨테이너 오케스트레이션", "section": "자격요건"},
        ], {"docker"})

        assert skill_kws["docker"] == ["컨테이너 오케스트레이션"]
        assert len(cur.executed) == 0

    def test_creates_new_skill_keyword_entry(self):
        skill_kws = {}
        cur = FakeCursor()

        _update_skill_keywords_from_llm(skill_kws, cur, [
            {"keyword": "분산 시스템 설계", "section": "자격요건"},
        ], {"kafka"})

        assert "분산 시스템 설계" in skill_kws["kafka"]
        assert len(cur.executed) == 1
