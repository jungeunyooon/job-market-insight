"""Unified LLM client — Gemini API first, Ollama fallback."""

import json
import logging
import os
import time
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Rate limiting for Gemini free tier (15 RPM)
_last_gemini_call: float = 0.0
_GEMINI_MIN_INTERVAL = float(os.getenv("GEMINI_MIN_INTERVAL", "4.0"))  # seconds between calls
_GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))


def generate(prompt: str, timeout: int = 30) -> str:
    """Send prompt to LLM. Tries Gemini first, then Ollama."""
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    ollama_host = os.getenv("OLLAMA_HOST", "")

    if gemini_api_key:
        return _gemini_generate(prompt, timeout, gemini_api_key, ollama_host)
    if ollama_host:
        return _ollama_generate(prompt, timeout, ollama_host)
    return ""


def _throttle_gemini():
    """Enforce minimum interval between Gemini API calls."""
    global _last_gemini_call
    now = time.monotonic()
    elapsed = now - _last_gemini_call
    if elapsed < _GEMINI_MIN_INTERVAL:
        sleep_time = _GEMINI_MIN_INTERVAL - elapsed
        logger.debug("Gemini throttle: %.1fs 대기", sleep_time)
        time.sleep(sleep_time)
    _last_gemini_call = time.monotonic()


def _gemini_generate(prompt: str, timeout: int, api_key: str, ollama_host: str) -> str:
    """Call Gemini REST API with retry on 429."""
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        },
    }).encode("utf-8")

    for attempt in range(_GEMINI_MAX_RETRIES):
        _throttle_gemini()

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            return ""
        except urllib.error.HTTPError as e:
            if e.code == 429:
                backoff = (2 ** attempt) * 5  # 5s, 10s, 20s
                logger.warning("Gemini 429 rate limit (attempt %d/%d), %ds 후 재시도",
                               attempt + 1, _GEMINI_MAX_RETRIES, backoff)
                time.sleep(backoff)
                continue
            logger.warning("Gemini API 실패: %s", e)
            break
        except Exception as e:
            logger.warning("Gemini API 실패: %s", e)
            break

    # Fallback to Ollama if available
    if ollama_host:
        return _ollama_generate(prompt, timeout, ollama_host)
    return ""


def _ollama_generate(prompt: str, timeout: int, ollama_host: str) -> str:
    """Call Ollama API."""
    ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    url = f"{ollama_host}/api/generate"
    body = json.dumps({
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 512},
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "")
