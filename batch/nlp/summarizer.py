"""Extractive text summarizer for tech blog content.

Extracts the most relevant sentences based on keyword density
and position in the text.
"""

from __future__ import annotations

import re


def extractive_summary(text: str, max_sentences: int = 3, min_length: int = 20) -> str:
    """Generate an extractive summary from text.

    Strategy:
    1. Split into sentences
    2. Score each sentence by:
       - Technical keyword density (code-related terms)
       - Position (first/last sentences get bonus)
       - Length (prefer medium-length sentences)
    3. Return top N sentences in original order
    """
    if not text or not text.strip():
        return ""

    # Split into sentences
    sentences = _split_sentences(text)
    if not sentences:
        return ""

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # Score sentences
    scored = []
    for i, sent in enumerate(sentences):
        if len(sent) < min_length:
            continue
        score = _score_sentence(sent, i, len(sentences))
        scored.append((i, sent, score))

    if not scored:
        return sentences[0] if sentences else ""

    # Select top N by score, return in original order
    scored.sort(key=lambda x: x[2], reverse=True)
    selected = sorted(scored[:max_sentences], key=lambda x: x[0])

    return " ".join(s[1] for s in selected)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling Korean and English."""
    # Clean HTML tags if any remain
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Split by sentence-ending punctuation
    # Handle both Korean (다. 요. etc.) and English (. ! ?)
    parts = re.split(r"(?<=[.!?。])\s+", text)

    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 5]


# Technical keywords that increase sentence relevance
_TECH_KEYWORDS = {
    "아키텍처", "architecture", "성능", "performance", "최적화", "optimization",
    "구현", "implementation", "도입", "적용", "개선", "해결",
    "api", "서버", "server", "데이터베이스", "database", "db",
    "캐시", "cache", "redis", "kafka", "kubernetes", "docker",
    "배포", "deploy", "ci/cd", "모니터링", "monitoring",
    "테스트", "test", "자동화", "automation",
    "마이크로서비스", "microservice", "msa", "분산", "distributed",
    "트래픽", "traffic", "확장", "scale", "scalability",
}


def _score_sentence(sentence: str, position: int, total: int) -> float:
    """Score a sentence for summary inclusion."""
    score = 0.0
    sent_lower = sentence.lower()

    # Technical keyword density
    words = sent_lower.split()
    if words:
        tech_count = sum(1 for w in words if any(kw in w for kw in _TECH_KEYWORDS))
        score += (tech_count / len(words)) * 10.0

    # Position bonus: first and last paragraphs tend to be summaries
    if position == 0:
        score += 3.0
    elif position == 1:
        score += 1.5
    elif position >= total - 2:
        score += 1.0

    # Length preference: medium-length sentences (50-200 chars)
    length = len(sentence)
    if 50 <= length <= 200:
        score += 2.0
    elif 30 <= length <= 300:
        score += 1.0

    # Bonus for sentences with numbers (often contain metrics/results)
    if re.search(r"\d+[%배만천억]|\d+\.\d+", sentence):
        score += 2.5

    return score
