"""LLM-based keyword extraction from tech blog posts.

Uses Ollama to extract contextual technical keywords from blog content —
capturing architecture patterns, implementation techniques, tooling choices etc.
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

_EXTRACT_PROMPT = """다음 기술 블로그 글에서 핵심 기술 키워드를 추출해주세요.

단순 기술명(Java, React 등)이 아닌, 구체적인 기술 역량/패턴/경험을 추출합니다:
- 예: "이벤트 드리븐 아키텍처", "모노레포 전환", "카나리 배포 전략", "쿼리 최적화"
- 예: "gRPC 마이그레이션", "실시간 데이터 파이프라인", "A/B 테스트 인프라"

각 키워드마다 어떤 맥락(architecture, implementation, devops, testing 등)에서 추출했는지 표시해주세요.

JSON 배열로만 응답하세요. 다른 텍스트 없이 JSON만 반환:
[{{"keyword": "키워드", "context": "architecture|implementation|devops|testing|data|infra"}}]

블로그 제목: {title}

블로그 내용:
{content}

JSON:"""


def llm_extract_blog_keywords(
    title: str,
    content: str,
    max_content_chars: int = 3000,
) -> list[dict]:
    """Ollama API를 호출하여 블로그 글에서 심층 기술 키워드를 추출한다.

    Returns:
        [{"keyword": str, "context": str}] 리스트. Ollama 미사용/오류 시 빈 리스트.
    """
    ollama_host = os.getenv("OLLAMA_HOST")
    if not ollama_host:
        return []

    title = (title or "").strip()
    content = (content or "").strip()
    if not title and not content:
        return []

    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n... (이하 생략)"

    prompt = _EXTRACT_PROMPT.format(title=title, content=content)

    try:
        url = f"{ollama_host.rstrip('/')}/api/generate"
        payload = json.dumps({
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 1000,
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

            keywords = json.loads(json_str)
            if not isinstance(keywords, list):
                return []

            # Validate and clean
            cleaned = []
            for item in keywords:
                if isinstance(item, dict) and "keyword" in item:
                    cleaned.append({
                        "keyword": str(item["keyword"]).strip(),
                        "context": str(item.get("context", "")).strip(),
                    })

            logger.info("블로그 LLM 키워드 추출 완료: %d개", len(cleaned))
            return cleaned

    except (URLError, OSError, json.JSONDecodeError, KeyError) as exc:
        logger.warning("Ollama 블로그 키워드 추출 실패: %s", exc)
        return []
    except Exception as exc:
        logger.warning("Ollama 블로그 키워드 추출 예외: %s", exc)
        return []
