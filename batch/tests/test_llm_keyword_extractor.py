"""Tests for LLM keyword extractor.

Uses unittest.mock to mock LLM API responses via llm_client.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.llm_keyword_extractor import llm_extract_keywords


MOCK_LLM_RESPONSE = json.dumps([
    {"keyword": "대규모 트래픽 처리 경험", "section": "자격요건"},
    {"keyword": "캐싱 전략 설계", "section": "자격요건"},
    {"keyword": "MSA 아키텍처 전환", "section": "우대사항"},
    {"keyword": "CI/CD 파이프라인 구축", "section": "우대사항"},
])

MOCK_LLM_RESPONSE_WITH_CODEBLOCK = f"```json\n{MOCK_LLM_RESPONSE}\n```"


def _make_mock_urlopen(response_text: str):
    """Ollama-format mock response for urllib.request.urlopen."""
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps({
        "response": response_text,
    }).encode("utf-8")
    return mock_resp


class TestLlmExtractKeywordsNoOllama:
    """LLM 미설정 시 빈 리스트 반환."""

    def test_returns_empty_without_ollama_host(self):
        with patch.dict("os.environ", {}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="Java 3년 이상",
            )
            assert result == []

    def test_returns_empty_with_empty_input(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords()
            assert result == []

    def test_returns_empty_with_blank_strings(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="   ",
                preferred_raw="",
            )
            assert result == []


class TestLlmExtractKeywordsWithMock:
    """LLM API 모킹하여 키워드 추출 테스트."""

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_extracts_keywords_from_requirements(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen(MOCK_LLM_RESPONSE)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="Java 기반 대규모 트래픽 처리 경험, 캐싱 전략 설계 가능자",
                preferred_raw="MSA 아키텍처 전환 경험, CI/CD 파이프라인 구축",
            )

        assert len(result) == 4
        assert result[0]["keyword"] == "대규모 트래픽 처리 경험"
        assert result[0]["section"] == "자격요건"
        assert result[2]["keyword"] == "MSA 아키텍처 전환"

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_codeblock_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen(MOCK_LLM_RESPONSE_WITH_CODEBLOCK)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="Spring Boot 기반 API 서버 개발",
            )

        assert len(result) == 4

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_invalid_json_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("이것은 JSON이 아닙니다")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="Java 경험 필수",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_empty_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="Python 개발 경험",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="Go 언어 경험",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_only_requirements_section(self, mock_urlopen):
        single_response = json.dumps([
            {"keyword": "REST API 설계", "section": "자격요건"},
        ])
        mock_urlopen.return_value = _make_mock_urlopen(single_response)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="REST API 설계 및 개발 경험",
            )

        assert len(result) == 1
        assert result[0]["keyword"] == "REST API 설계"

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_truncates_long_content(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("[]")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_keywords(
                requirements_raw="A" * 5000,
                max_content_chars=100,
            )

        assert result == []
        # Verify the call was made (content was truncated, not skipped)
        mock_urlopen.assert_called_once()
