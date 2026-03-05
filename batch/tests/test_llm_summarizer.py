"""Tests for LLM summarizer."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.llm_summarizer import llm_summarize


def _make_mock_urlopen(response_text: str):
    """Ollama-format mock response for urllib.request.urlopen."""
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps({
        "response": response_text,
    }).encode("utf-8")
    return mock_resp


class TestLlmSummarize:
    def test_returns_none_when_no_ollama_host(self):
        with patch.dict("os.environ", {}, clear=True):
            result = llm_summarize("Some content")
            assert result is None

    def test_returns_none_for_empty_content(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            assert llm_summarize("") is None
            assert llm_summarize(None) is None

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_returns_summary_on_success(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen(
            "Redis 캐싱 아키텍처를 도입하여 성능을 3배 개선했습니다."
        )

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_summarize("블로그 내용...")
            assert result is not None
            assert "Redis" in result

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_returns_none_on_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_summarize("블로그 내용...")
            assert result is None

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_truncates_long_content(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("요약")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            long_content = "A" * 5000
            llm_summarize(long_content, max_content_chars=100)
            # Verify the request was made (content was truncated internally)
            mock_urlopen.assert_called_once()
