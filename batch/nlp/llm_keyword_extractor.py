"""LLM-based keyword extraction from job posting structured fields.

Uses LLM to extract contextual technical keywords that go beyond
simple skill name matching — capturing domain-specific requirements
like '대규모 트래픽 처리', '캐싱 전략', 'MSA 전환 경험' etc.
"""

from __future__ import annotations

import json
import logging
import os

from nlp.llm_client import generate as llm_generate

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))

_EXTRACT_PROMPT = """다음 채용 공고의 자격요건/우대사항에서 핵심 기술 키워드를 추출해주세요.

단순 기술명(Java, Spring 등)이 아닌, 구체적인 기술 역량/경험을 추출합니다:
- 예: "대규모 트래픽 처리 경험", "캐싱 전략 설계", "MSA 아키텍처 전환", "CI/CD 파이프라인 구축"
- 예: "TTL 설정 최적화", "분산 시스템 설계", "데이터 파이프라인 구축", "코드 리뷰 문화"

각 키워드마다 어느 섹션(자격요건/우대사항/담당업무)에서 추출했는지 표시해주세요.

JSON 배열로만 응답하세요. 다른 텍스트 없이 JSON만 반환:
[{{"keyword": "키워드", "section": "자격요건|우대사항|담당업무"}}]

공고 내용:
{content}

JSON:"""


def llm_extract_keywords(
    requirements_raw: str | None = None,
    preferred_raw: str | None = None,
    responsibilities_raw: str | None = None,
    max_content_chars: int = 3000,
) -> list[dict]:
    """LLM API를 호출하여 채용 공고에서 심층 기술 키워드를 추출한다.

    Returns:
        [{"keyword": str, "section": str}] 리스트. LLM 미사용/오류 시 빈 리스트.
    """
    sections = []
    if requirements_raw and requirements_raw.strip():
        sections.append(f"[자격요건]\n{requirements_raw.strip()}")
    if preferred_raw and preferred_raw.strip():
        sections.append(f"[우대사항]\n{preferred_raw.strip()}")
    if responsibilities_raw and responsibilities_raw.strip():
        sections.append(f"[담당업무]\n{responsibilities_raw.strip()}")

    if not sections:
        return []

    content = "\n\n".join(sections)
    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n... (이하 생략)"

    prompt = _EXTRACT_PROMPT.format(content=content)

    try:
        raw_response = llm_generate(prompt, timeout=DEFAULT_TIMEOUT).strip()
        if not raw_response:
            return []

        # Parse JSON from response (handle markdown code blocks)
        json_str = raw_response
        if "```" in json_str:
            # Extract JSON from code block
            start = json_str.find("[")
            end = json_str.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]

        keywords = json.loads(json_str)
        if not isinstance(keywords, list):
            return []

        # Validate and clean
        cleaned = []
        for item in keywords:
            if isinstance(item, dict) and "keyword" in item:
                cleaned.append({
                    "keyword": str(item["keyword"]).strip(),
                    "section": str(item.get("section", "")).strip(),
                })

        logger.info("LLM 키워드 추출 완료: %d개", len(cleaned))
        return cleaned

    except (json.JSONDecodeError, KeyError) as exc:
        logger.warning("LLM 키워드 추출 실패: %s", exc)
        return []
    except Exception as exc:
        logger.warning("LLM 키워드 추출 예외: %s", exc)
        return []
