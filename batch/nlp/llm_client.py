"""Unified LLM client — Gemini API first, Ollama fallback."""

import json
import logging
import os
import time
import urllib.request
import urllib.error
from typing import Dict, List

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Rate limiting for Gemini free tier (15 RPM per key)
_GEMINI_MIN_INTERVAL = float(os.getenv("GEMINI_MIN_INTERVAL", "8.0"))  # seconds per key
_GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))

# Per-key state for round-robin rotation
_gemini_keys: List[str] = []
_last_call_per_key: Dict[str, float] = {}
_key_index: int = 0
_keys_logged: bool = False


def _init_keys() -> None:
    """Parse GEMINI_API_KEY env var (comma-separated) into _gemini_keys."""
    global _gemini_keys, _keys_logged
    raw = os.getenv("GEMINI_API_KEY", "")
    _gemini_keys = [k.strip() for k in raw.split(",") if k.strip()]
    if _gemini_keys and not _keys_logged:
        logger.info("Gemini API keys available: %d (effective interval: %.1fs)",
                    len(_gemini_keys), _GEMINI_MIN_INTERVAL / len(_gemini_keys))
        _keys_logged = True


def _next_key() -> str:
    """Return the next API key in round-robin order."""
    global _key_index
    if not _gemini_keys:
        _init_keys()
    key = _gemini_keys[_key_index % len(_gemini_keys)]
    _key_index += 1
    return key


def _throttle_gemini(key: str) -> None:
    """Enforce minimum interval for a specific API key."""
    now = time.monotonic()
    last = _last_call_per_key.get(key, 0.0)
    elapsed = now - last
    if elapsed < _GEMINI_MIN_INTERVAL:
        sleep_time = _GEMINI_MIN_INTERVAL - elapsed
        logger.debug("Gemini throttle (key ...%s): %.1fs 대기", key[-4:], sleep_time)
        time.sleep(sleep_time)
    _last_call_per_key[key] = time.monotonic()


def generate(prompt: str, timeout: int = 30) -> str:
    """Send prompt to LLM. Tries Gemini first, then Ollama."""
    _init_keys()
    ollama_host = os.getenv("OLLAMA_HOST", "")

    if _gemini_keys:
        return _gemini_generate(prompt, timeout, ollama_host)
    if ollama_host:
        return _ollama_generate(prompt, timeout, ollama_host)
    return ""


def _gemini_generate(prompt: str, timeout: int, ollama_host: str) -> str:
    """Call Gemini REST API with retry on 429, rotating API keys round-robin."""
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        },
    }).encode("utf-8")

    for attempt in range(_GEMINI_MAX_RETRIES):
        api_key = _next_key()
        _throttle_gemini(api_key)

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{gemini_model}:generateContent?key={api_key}"
        )
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
