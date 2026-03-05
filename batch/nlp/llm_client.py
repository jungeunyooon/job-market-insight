"""Unified LLM client — Gemini API first, Ollama fallback."""

import json
import logging
import os
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def generate(prompt: str, timeout: int = 30) -> str:
    """Send prompt to LLM. Tries Gemini first, then Ollama."""
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    ollama_host = os.getenv("OLLAMA_HOST", "")

    if gemini_api_key:
        return _gemini_generate(prompt, timeout, gemini_api_key, ollama_host)
    if ollama_host:
        return _ollama_generate(prompt, timeout, ollama_host)
    return ""


def _gemini_generate(prompt: str, timeout: int, api_key: str, ollama_host: str) -> str:
    """Call Gemini REST API."""
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        },
    }).encode("utf-8")

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
    except Exception as e:
        logger.warning("Gemini API 실패: %s", e)
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
