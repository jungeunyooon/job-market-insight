"""LLM-based blog summarizer.

Calls a Gemini or Ollama LLM to generate Korean technical summaries.
Falls back gracefully if no LLM is available.
"""

from __future__ import annotations

import logging
import os

from nlp.llm_client import generate as llm_generate

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))

_SUMMARY_PROMPT = """다음 기술 블로그 글을 읽고 핵심 기술적 인사이트를 한국어로 3-5문장으로 요약해주세요.
요약에는 다음을 포함해주세요:
- 어떤 기술적 문제를 해결했는지
- 사용된 기술 스택이나 접근 방식
- 주요 성과나 결과 (수치가 있다면 포함)

블로그 내용:
{content}

요약:"""


def llm_summarize(content: str, max_content_chars: int = 3000) -> str | None:
    """LLM API를 호출하여 블로그 콘텐츠를 요약한다.

    Returns:
        요약 문자열. LLM 미사용/오류 시 None 반환 (caller가 fallback 처리).
    """
    if not content or not content.strip():
        return None

    # Truncate very long content to avoid timeout
    truncated = content[:max_content_chars]
    if len(content) > max_content_chars:
        truncated += "\n... (이하 생략)"

    prompt = _SUMMARY_PROMPT.format(content=truncated)

    try:
        summary = llm_generate(prompt, timeout=DEFAULT_TIMEOUT).strip()
        if summary:
            logger.info("LLM 요약 생성 완료 (%d chars)", len(summary))
            return summary
        return None
    except Exception as exc:
        logger.warning("LLM 요약 실패, extractive fallback 사용: %s", exc)
        return None
