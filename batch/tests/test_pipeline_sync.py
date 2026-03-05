"""Tests for pipeline sync: crawl_log writing and retry logic."""

from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# psycopg2가 로컬에 설치되어 있지 않을 수 있으므로 mock으로 대체
if "psycopg2" not in sys.modules:
    _mock_pg = ModuleType("psycopg2")
    _mock_pg.connect = MagicMock()  # type: ignore[attr-defined]
    sys.modules["psycopg2"] = _mock_pg

    _mock_extras = ModuleType("psycopg2.extras")
    _mock_extras.Json = lambda x: x  # type: ignore[attr-defined]
    sys.modules["psycopg2.extras"] = _mock_extras

from pipeline.sync import CrawlStatusLiteral, DevPulseSync, SyncStats


class TestSyncStats:
    def test_defaults(self) -> None:
        stats = SyncStats()
        assert stats.crawled == 0
        assert stats.inserted == 0
        assert stats.updated == 0
        assert stats.failed == 0

    def test_custom_values(self) -> None:
        stats = SyncStats(crawled=10, inserted=5, updated=3, failed=2)
        assert stats.crawled == 10
        assert stats.inserted == 5
        assert stats.updated == 3
        assert stats.failed == 2


class TestLogCrawlExecution:
    """log_crawl_execution이 crawl_log 테이블에 올바른 값을 INSERT하는지 검증."""

    @patch("pipeline.sync.psycopg2.connect")
    def test_log_crawl_execution_inserts_row(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = mock_conn

        sync = DevPulseSync.__new__(DevPulseSync)
        sync._conn = mock_conn
        sync._seed_skills = []
        sync._seed_companies = []
        sync._alias_to_company = {}

        started = datetime(2026, 3, 5, 10, 0, 0, tzinfo=timezone.utc)
        finished = datetime(2026, 3, 5, 10, 0, 5, tzinfo=timezone.utc)
        stats = SyncStats(crawled=100, inserted=80, updated=15, failed=5)

        sync.log_crawl_execution(
            source_type="JOB_POSTING",
            source_name="WantedAPICrawler",
            status="SUCCESS",
            stats=stats,
            started_at=started,
            finished_at=finished,
            error_message=None,
        )

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO crawl_log" in sql
        assert params[0] == "JOB_POSTING"  # source_type
        assert params[1] == "WantedAPICrawler"  # source_name
        assert params[2] == "SUCCESS"  # status
        assert params[3] == 100  # items_collected
        assert params[4] == 80  # items_new
        assert params[5] == 0  # items_duplicate (100 - 80 - 15 - 5 = 0)
        assert params[6] is None  # error_message
        assert params[7] == 5000  # duration_ms (5 seconds)
        mock_conn.commit.assert_called()

    @patch("pipeline.sync.psycopg2.connect")
    def test_log_crawl_execution_calculates_duplicates(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = mock_conn

        sync = DevPulseSync.__new__(DevPulseSync)
        sync._conn = mock_conn
        sync._seed_skills = []
        sync._seed_companies = []
        sync._alias_to_company = {}

        started = datetime(2026, 3, 5, 10, 0, 0, tzinfo=timezone.utc)
        finished = datetime(2026, 3, 5, 10, 0, 2, tzinfo=timezone.utc)
        # 50 crawled, 10 inserted, 5 updated, 0 failed → 35 duplicates
        stats = SyncStats(crawled=50, inserted=10, updated=5, failed=0)

        sync.log_crawl_execution("BLOG", "TechBlogCrawler", "SUCCESS", stats, started, finished)

        params = mock_cursor.execute.call_args[0][1]
        assert params[5] == 35  # items_duplicate

    @patch("pipeline.sync.psycopg2.connect")
    def test_log_crawl_execution_negative_duplicates_clamped_to_zero(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = mock_conn

        sync = DevPulseSync.__new__(DevPulseSync)
        sync._conn = mock_conn
        sync._seed_skills = []
        sync._seed_companies = []
        sync._alias_to_company = {}

        started = datetime(2026, 3, 5, 10, 0, 0, tzinfo=timezone.utc)
        finished = datetime(2026, 3, 5, 10, 0, 1, tzinfo=timezone.utc)
        # Edge: failed > crawled (shouldn't happen, but defensive)
        stats = SyncStats(crawled=5, inserted=3, updated=3, failed=2)

        sync.log_crawl_execution("TREND", "GeekNewsCrawler", "PARTIAL", stats, started, finished)

        params = mock_cursor.execute.call_args[0][1]
        assert params[5] == 0  # clamped to 0

    @patch("pipeline.sync.psycopg2.connect")
    def test_log_crawl_execution_swallows_db_error(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB connection lost")
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = mock_conn

        sync = DevPulseSync.__new__(DevPulseSync)
        sync._conn = mock_conn
        sync._seed_skills = []
        sync._seed_companies = []
        sync._alias_to_company = {}

        started = datetime(2026, 3, 5, 10, 0, 0, tzinfo=timezone.utc)
        finished = datetime(2026, 3, 5, 10, 0, 1, tzinfo=timezone.utc)
        stats = SyncStats(crawled=10, inserted=5, updated=5, failed=0)

        # Should NOT raise
        sync.log_crawl_execution("JOB_POSTING", "test", "SUCCESS", stats, started, finished)


class TestSyncWithRetry:
    """_sync_with_retry의 재시도/백오프/장애 격리 검증."""

    def test_success_on_first_attempt(self) -> None:
        from main import _sync_with_retry

        mock_fn = MagicMock(return_value=SyncStats(crawled=10, inserted=5, updated=5))
        stats, ok = _sync_with_retry("test", mock_fn, [1, 2, 3], "test_source")
        assert ok is True
        assert stats.crawled == 10
        mock_fn.assert_called_once_with([1, 2, 3], source_name="test_source")

    def test_success_on_retry(self) -> None:
        from main import _sync_with_retry

        mock_fn = MagicMock(
            side_effect=[
                Exception("temporary failure"),
                SyncStats(crawled=5, inserted=3, updated=2),
            ]
        )
        with patch("main.time.sleep"):  # skip actual sleep
            stats, ok = _sync_with_retry("test", mock_fn, [], "test_source")

        assert ok is True
        assert stats.inserted == 3
        assert mock_fn.call_count == 2

    def test_failure_after_all_retries(self) -> None:
        from main import _sync_with_retry

        mock_fn = MagicMock(side_effect=Exception("persistent failure"))
        with patch("main.time.sleep"):
            stats, ok = _sync_with_retry("test", mock_fn, [], "test_source")

        assert ok is False
        assert stats.crawled == 0
        assert mock_fn.call_count == 3  # 1 initial + 2 retries

    def test_retry_uses_exponential_backoff(self) -> None:
        from main import _sync_with_retry

        mock_fn = MagicMock(side_effect=Exception("fail"))
        with patch("main.time.sleep") as mock_sleep:
            _sync_with_retry("test", mock_fn, [], "test_source")

        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2)  # 1st retry: 2s
        mock_sleep.assert_any_call(4)  # 2nd retry: 4s


class TestExtractMatchedKeywords:
    """_extract_matched_keywords가 스킬의 세부 키워드를 설명에서 올바르게 추출하는지 검증."""

    def _make_sync(self, seed_skills: list[dict]) -> "DevPulseSync":
        sync = DevPulseSync.__new__(DevPulseSync)
        sync._conn = MagicMock()
        sync._seed_skills = seed_skills
        sync._seed_companies = []
        sync._alias_to_company = {}
        sync._skill_keywords = {
            str(s.get("name", "")).strip().lower(): [
                str(k).strip() for k in s.get("keywords", []) if str(k).strip()
            ]
            for s in seed_skills
            if str(s.get("name", "")).strip()
        }
        return sync

    def test_extracts_matching_keywords(self) -> None:
        seed = [{"name": "Redis", "keywords": ["캐싱 전략", "TTL"], "aliases": [], "category": "infra", "source_scope": "JOB_POSTING"}]
        sync = self._make_sync(seed)
        description = "캐싱 전략을 적용하여 성능을 개선하였습니다."
        result = sync._extract_matched_keywords("Redis", description)
        assert result == ["캐싱 전략"]

    def test_no_keywords_found(self) -> None:
        seed = [{"name": "Redis", "keywords": ["캐싱 전략", "TTL"], "aliases": [], "category": "infra", "source_scope": "JOB_POSTING"}]
        sync = self._make_sync(seed)
        description = "Kafka를 이용한 메시지 큐 처리 경험이 있으신 분"
        result = sync._extract_matched_keywords("Redis", description)
        assert result == []

    def test_case_insensitive(self) -> None:
        seed = [{"name": "Redis", "keywords": ["캐싱 전략", "TTL"], "aliases": [], "category": "infra", "source_scope": "JOB_POSTING"}]
        sync = self._make_sync(seed)
        description = "ttl 설정 경험 필요"
        result = sync._extract_matched_keywords("Redis", description)
        assert result == ["TTL"]
