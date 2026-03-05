"""LLM-based blog summarizer using Ollama API.

Calls a local Ollama instance to generate Korean technical summaries.
Falls back gracefully if Ollama is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# Default model — lightweight, good for Korean text
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
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
    """Ollama API를 호출하여 블로그 콘텐츠를 요약한다.

    Returns:
        요약 문자열. Ollama 미사용/오류 시 None 반환 (caller가 fallback 처리).
    """
    ollama_host = os.getenv("OLLAMA_HOST")
    if not ollama_host:
        return None

    if not content or not content.strip():
        return None

    # Truncate very long content to avoid timeout
    truncated = content[:max_content_chars]
    if len(content) > max_content_chars:
        truncated += "\n... (이하 생략)"

    prompt = _SUMMARY_PROMPT.format(content=truncated)

    try:
        url = f"{ollama_host.rstrip('/')}/api/generate"
        payload = json.dumps({
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 500,
            },
        }).encode("utf-8")

        req = Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            summary = result.get("response", "").strip()
            if summary:
                logger.info("LLM 요약 생성 완료 (%d chars)", len(summary))
                return summary
            return None
    except (URLError, OSError, json.JSONDecodeError, KeyError) as exc:
        logger.warning("Ollama 요약 실패, extractive fallback 사용: %s", exc)
        return None
    except Exception as exc:
        logger.warning("Ollama 예외, extractive fallback 사용: %s", exc)
        return None
