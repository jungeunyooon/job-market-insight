"""Tests for topic extractor."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.skill_matcher import SkillMatcher
from nlp.topic_extractor import TopicExtractor


SAMPLE_SKILLS = [
    {"name": "Kafka", "aliases": ["Apache Kafka"], "category": "messaging", "source_scope": "BOTH"},
    {"name": "Spring Boot", "aliases": ["SpringBoot"], "category": "framework", "source_scope": "BOTH"},
    {"name": "Java", "aliases": [], "category": "language", "source_scope": "BOTH"},
    {"name": "Kubernetes", "aliases": ["K8s", "쿠버네티스"], "category": "devops", "source_scope": "BOTH"},
    {"name": "Docker", "aliases": ["도커"], "category": "devops", "source_scope": "BOTH"},
    {"name": "MSA", "aliases": ["Microservice", "마이크로서비스"], "category": "concept", "source_scope": "BOTH"},
    {"name": "Redis", "aliases": ["레디스"], "category": "database", "source_scope": "BOTH"},
]


@pytest.fixture
def extractor() -> TopicExtractor:
    matcher = SkillMatcher(SAMPLE_SKILLS)
    return TopicExtractor(matcher)


class TestExtractFromTitle:
    def test_single_topic(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_from_title("Kafka 도입기: 실시간 데이터 파이프라인 구축")
        assert len(topics) >= 1
        names = [t.skill_name for t in topics]
        assert "Kafka" in names
        assert all(t.source == "title" for t in topics)

    def test_multiple_topics(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_from_title("Spring Boot에서 Kafka와 Redis를 활용한 MSA 구축")
        names = [t.skill_name for t in topics]
        assert "Spring Boot" in names
        assert "Kafka" in names
        assert "Redis" in names
        assert "MSA" in names

    def test_no_topics(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_from_title("우리 팀의 코드 리뷰 문화를 소개합니다")
        assert len(topics) == 0


class TestExtractFromTags:
    def test_tags_extraction(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_from_tags(["Kafka", "Java", "Backend"])
        names = [t.skill_name for t in topics]
        assert "Kafka" in names
        assert "Java" in names
        assert all(t.source == "tags" for t in topics)

    def test_deduplication_in_tags(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_from_tags(["Kafka", "Apache Kafka"])
        names = [t.skill_name for t in topics]
        assert names.count("Kafka") == 1


class TestExtractAll:
    def test_title_and_tags_merged(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_all(
            title="Kafka 도입기",
            tags=["Java", "Backend"],
        )
        names = [t.skill_name for t in topics]
        assert "Kafka" in names
        assert "Java" in names

    def test_dedup_across_sources(self, extractor: TopicExtractor) -> None:
        """Title과 tags에 동일 스킬이 있으면 title 우선."""
        topics = extractor.extract_all(
            title="Kafka와 Spring Boot 활용",
            tags=["Kafka", "Spring Boot"],
        )
        names = [t.skill_name for t in topics]
        assert names.count("Kafka") == 1
        # Kafka should be from title (first source)
        kafka_topic = next(t for t in topics if t.skill_name == "Kafka")
        assert kafka_topic.source == "title"

    def test_content_extraction(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_all(
            title="우리 팀의 인프라 이야기",
            content="Docker와 Kubernetes를 활용하여 배포 자동화를 구현했습니다.",
        )
        names = [t.skill_name for t in topics]
        assert "Docker" in names
        assert "Kubernetes" in names
        docker_topic = next(t for t in topics if t.skill_name == "Docker")
        assert docker_topic.source == "content"

    def test_empty_input(self, extractor: TopicExtractor) -> None:
        topics = extractor.extract_all(title="", tags=[], content="")
        assert len(topics) == 0
