"""Shared test fixtures for batch tests."""

import pytest

from nlp.skill_matcher import SkillMatcher


SAMPLE_SKILLS = [
    {
        "name": "Java",
        "name_ko": "자바",
        "category": "language",
        "aliases": ["java"],
        "source_scope": "BOTH",
    },
    {
        "name": "Spring Boot",
        "name_ko": "스프링 부트",
        "category": "framework",
        "aliases": ["SpringBoot", "스프링부트", "Spring-Boot", "spring boot"],
        "source_scope": "BOTH",
    },
    {
        "name": "Kubernetes",
        "name_ko": "쿠버네티스",
        "category": "devops",
        "aliases": ["K8s", "k8s", "쿠버네티스", "쿠베", "Kube"],
        "source_scope": "BOTH",
    },
    {
        "name": "Kafka",
        "name_ko": "카프카",
        "category": "messaging",
        "aliases": ["Apache Kafka", "kafka"],
        "source_scope": "BOTH",
    },
    {
        "name": "Docker",
        "name_ko": "도커",
        "category": "devops",
        "aliases": ["docker", "도커"],
        "source_scope": "BOTH",
    },
    {
        "name": "AWS",
        "name_ko": None,
        "category": "devops",
        "aliases": ["Amazon Web Services", "aws"],
        "source_scope": "BOTH",
    },
    {
        "name": "React",
        "name_ko": "리액트",
        "category": "framework",
        "aliases": ["ReactJS", "React.js", "리액트"],
        "source_scope": "BOTH",
    },
    {
        "name": "GitHub Copilot",
        "name_ko": None,
        "category": "ai_ml_devtool",
        "aliases": ["Copilot", "코파일럿", "깃허브 코파일럿"],
        "source_scope": "BOTH",
    },
    {
        "name": "vibe coding",
        "name_ko": "바이브 코딩",
        "category": "ai_ml_devtool",
        "aliases": ["바이브코딩"],
        "source_scope": "TREND",
    },
    {
        "name": "LLM",
        "name_ko": None,
        "category": "ai_ml_model",
        "aliases": ["Large Language Model", "대규모 언어 모델"],
        "source_scope": "BOTH",
    },
]


@pytest.fixture
def skill_matcher() -> SkillMatcher:
    """Create a SkillMatcher loaded with sample skills."""
    matcher = SkillMatcher()
    matcher.load_skills_from_list(SAMPLE_SKILLS)
    return matcher
