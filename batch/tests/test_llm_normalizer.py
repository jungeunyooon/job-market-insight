"""Tests for LLM requirement normalizer.

Uses unittest.mock to mock LLM API responses via llm_client.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.llm_normalizer import llm_normalize_requirements


MOCK_NORMALIZED_RESPONSE = json.dumps([
    {"original": "Java 경험 3년 이상", "normalized": "Java 실무 경험", "category": "technical"},
    {"original": "대규모 트래픽 처리 경험", "normalized": "대규모 트래픽 처리 경험", "category": "experience"},
    {"original": "AWS 인프라 운영 가능자", "normalized": "AWS 인프라 운영 경험", "category": "technical"},
    {"original": "원활한 커뮤니케이션", "normalized": "커뮤니케이션 역량", "category": "soft_skill"},
])


def _make_mock_urlopen(response_text: str):
    """Ollama-format mock response for urllib.request.urlopen."""
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps({
        "response": response_text,
    }).encode("utf-8")
    return mock_resp


class TestLlmNormalizerNoOllama:
    """LLM 미설정 시 빈 리스트 반환."""

    def test_returns_empty_without_ollama_host(self):
        with patch.dict("os.environ", {}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Java 3년 이상",
            )
            assert result == []

    def test_returns_empty_with_no_input(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements()
            assert result == []

    def test_returns_empty_with_blank_strings(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="  ",
                preferred_raw="",
            )
            assert result == []


class TestLlmNormalizerWithMock:
    """LLM API 모킹하여 정규화 테스트."""

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_normalizes_requirements(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen(MOCK_NORMALIZED_RESPONSE)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Java 경험 3년 이상\n대규모 트래픽 처리 경험",
                preferred_raw="AWS 인프라 운영 가능자\n원활한 커뮤니케이션",
            )

        assert len(result) == 4
        assert result[0]["original"] == "Java 경험 3년 이상"
        assert result[0]["normalized"] == "Java 실무 경험"
        assert result[0]["category"] == "technical"
        assert result[3]["category"] == "soft_skill"

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_codeblock_response(self, mock_urlopen):
        codeblock = f"```json\n{MOCK_NORMALIZED_RESPONSE}\n```"
        mock_urlopen.return_value = _make_mock_urlopen(codeblock)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Spring Boot 개발 경험",
            )

        assert len(result) == 4

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_invalid_json(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("유효하지 않은 응답입니다")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Python 경험",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_empty_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Go 개발 경험",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Kubernetes 운영 경험",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_only_requirements_no_preferred(self, mock_urlopen):
        single = json.dumps([
            {"original": "Docker 경험", "normalized": "Docker 활용 경험", "category": "technical"},
        ])
        mock_urlopen.return_value = _make_mock_urlopen(single)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="Docker 경험 필수",
            )

        assert len(result) == 1
        assert result[0]["normalized"] == "Docker 활용 경험"

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_truncates_long_content(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("[]")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_normalize_requirements(
                requirements_raw="A" * 5000,
                max_content_chars=100,
            )

        assert result == []
        mock_urlopen.assert_called_once()
