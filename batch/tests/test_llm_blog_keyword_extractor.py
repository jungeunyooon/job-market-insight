"""Tests for LLM blog keyword extractor.

Uses unittest.mock to mock LLM API responses via llm_client.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.llm_blog_keyword_extractor import llm_extract_blog_keywords


MOCK_LLM_RESPONSE = json.dumps([
    {"keyword": "이벤트 드리븐 아키텍처", "context": "architecture"},
    {"keyword": "카프카 컨슈머 최적화", "context": "implementation"},
    {"keyword": "카나리 배포 전략", "context": "devops"},
    {"keyword": "부하 테스트 자동화", "context": "testing"},
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


class TestLlmExtractBlogKeywordsNoOllama:
    """LLM 미설정 시 빈 리스트 반환."""

    def test_returns_empty_without_ollama_host(self):
        with patch.dict("os.environ", {}, clear=True):
            result = llm_extract_blog_keywords(
                title="Kafka 컨슈머 최적화 사례",
                content="대규모 메시지를 처리하기 위해...",
            )
            assert result == []

    def test_returns_empty_with_empty_input(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(title="", content="")
            assert result == []

    def test_returns_empty_with_blank_strings(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(title="   ", content="   ")
            assert result == []

    def test_returns_empty_with_none_inputs(self):
        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(title=None, content=None)
            assert result == []


class TestLlmExtractBlogKeywordsWithMock:
    """LLM API 모킹하여 키워드 추출 테스트."""

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_extracts_keywords_from_blog(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen(MOCK_LLM_RESPONSE)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="Kafka 컨슈머 최적화 사례",
                content="대규모 메시지를 처리하기 위해 이벤트 드리븐 아키텍처를 도입했습니다.",
            )

        assert len(result) == 4
        assert result[0]["keyword"] == "이벤트 드리븐 아키텍처"
        assert result[0]["context"] == "architecture"
        assert result[2]["keyword"] == "카나리 배포 전략"
        assert result[2]["context"] == "devops"

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_codeblock_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen(MOCK_LLM_RESPONSE_WITH_CODEBLOCK)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="모노레포 전환기",
                content="여러 서비스를 하나의 레포지토리로 통합한 과정을 공유합니다.",
            )

        assert len(result) == 4

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_invalid_json_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("이것은 JSON이 아닙니다")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="기술 블로그",
                content="내용입니다",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_empty_response(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="블로그 제목",
                content="블로그 내용",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_handles_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="기술 블로그",
                content="내용",
            )

        assert result == []

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_title_only_extraction(self, mock_urlopen):
        single_response = json.dumps([
            {"keyword": "gRPC 마이그레이션", "context": "architecture"},
        ])
        mock_urlopen.return_value = _make_mock_urlopen(single_response)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="gRPC 마이그레이션 후기",
                content="",
            )

        assert len(result) == 1
        assert result[0]["keyword"] == "gRPC 마이그레이션"

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_truncates_long_content(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("[]")

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="긴 블로그",
                content="A" * 5000,
                max_content_chars=100,
            )

        assert result == []
        mock_urlopen.assert_called_once()

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_context_field_defaults_to_empty(self, mock_urlopen):
        """context 필드 없는 응답 처리."""
        response = json.dumps([{"keyword": "실시간 파이프라인"}])
        mock_urlopen.return_value = _make_mock_urlopen(response)

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="데이터 파이프라인",
                content="실시간 데이터 처리를 구현했습니다.",
            )

        assert len(result) == 1
        assert result[0]["context"] == ""

    @patch("nlp.llm_client.urllib.request.urlopen")
    def test_non_list_response_returns_empty(self, mock_urlopen):
        """JSON 응답이 리스트가 아닌 경우."""
        mock_urlopen.return_value = _make_mock_urlopen('{"keyword": "test"}')

        with patch.dict("os.environ", {"OLLAMA_HOST": "http://localhost:11434"}, clear=True):
            result = llm_extract_blog_keywords(
                title="테스트",
                content="내용",
            )

        assert result == []
