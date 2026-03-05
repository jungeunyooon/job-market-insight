"""LLM-based requirement normalization.

Uses Ollama to normalize different wordings of the same job requirement
into canonical forms for better trend analysis.

Example:
    "Java 경험 3년 이상", "Java 기반 백엔드 개발" → "Java 실무 경험"
    "대규모 트래픽 처리", "고트래픽 서비스 운영" → "대규모 트래픽 처리 경험"
"""

from __future__ import annotations

import json
import logging
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
DEFAULT_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))

_NORMALIZE_PROMPT = """다음 채용 공고의 자격요건/우대사항 텍스트를 분석하여, 각 요구사항을 정규화된 형태로 변환해주세요.

규칙:
1. 비슷한 의미의 요구사항은 하나의 정규화된 표현으로 통일
2. 경력 연수는 제거하고 핵심 역량만 남김 (예: "Java 3년 이상" → "Java 실무 경험")
3. 카테고리 분류: technical(기술), experience(경험), soft_skill(소프트스킬), education(학력), domain(도메인)
4. 간결하고 명확한 한국어 표현 사용

JSON 배열로만 응답하세요:
[{{"original": "원문 텍스트", "normalized": "정규화된 표현", "category": "카테고리"}}]

자격요건/우대사항:
{content}

JSON:"""


def llm_normalize_requirements(
    requirements_raw: str | None = None,
    preferred_raw: str | None = None,
    max_content_chars: int = 3000,
) -> list[dict]:
    """Ollama API를 호출하여 자격요건/우대사항을 정규화한다.

    Returns:
        [{"original": str, "normalized": str, "category": str}] 리스트.
        Ollama 미사용/오류 시 빈 리스트.
    """
    ollama_host = os.getenv("OLLAMA_HOST")
    if not ollama_host:
        return []

    sections = []
    if requirements_raw and requirements_raw.strip():
        sections.append(f"[자격요건]\n{requirements_raw.strip()}")
    if preferred_raw and preferred_raw.strip():
        sections.append(f"[우대사항]\n{preferred_raw.strip()}")

    if not sections:
        return []

    content = "\n\n".join(sections)
    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n... (이하 생략)"

    prompt = _NORMALIZE_PROMPT.format(content=content)

    try:
        url = f"{ollama_host.rstrip('/')}/api/generate"
        payload = json.dumps({
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 1500,
            },
        }).encode("utf-8")

        req = Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            raw_response = result.get("response", "").strip()
            if not raw_response:
                return []

            # Parse JSON from response (handle markdown code blocks)
            json_str = raw_response
            if "```" in json_str:
                start = json_str.find("[")
                end = json_str.rfind("]") + 1
                if start >= 0 and end > start:
                    json_str = json_str[start:end]

            normalized = json.loads(json_str)
            if not isinstance(normalized, list):
                return []

            # Validate and clean
            cleaned = []
            for item in normalized:
                if isinstance(item, dict) and "original" in item and "normalized" in item:
                    cleaned.append({
                        "original": str(item["original"]).strip(),
                        "normalized": str(item["normalized"]).strip(),
                        "category": str(item.get("category", "technical")).strip(),
                    })

            logger.info("LLM 요구사항 정규화 완료: %d개", len(cleaned))
            return cleaned

    except (URLError, OSError, json.JSONDecodeError, KeyError) as exc:
        logger.warning("Ollama 정규화 실패: %s", exc)
        return []
    except Exception as exc:
        logger.warning("Ollama 정규화 예외: %s", exc)
        return []
