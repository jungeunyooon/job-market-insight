"""Tests for trend snapshot saving logic in sync pipeline."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

psycopg2 = pytest.importorskip("psycopg2", reason="psycopg2 not installed")

from pipeline.sync import DevPulseSync


class TestSaveTrendSnapshot:
    """_save_trend_snapshot 메서드 테스트."""

    def _make_sync(self):
        """DevPulseSync를 DB 연결 없이 생성 (메서드 단위 테스트용)."""
        with patch.object(DevPulseSync, "__init__", lambda self: None):
            sync = DevPulseSync()
            return sync

    def test_saves_snapshot_for_geeknews(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.fetchall.return_value = [
            ("LangChain", 47),
            ("Rust", 35),
            ("Kafka", 12),
        ]

        sync._save_trend_snapshot(cur, "geeknews", top_n=20)

        # SELECT 쿼리 1번 + INSERT 3번 = 4번 execute
        assert cur.execute.call_count == 4
        # 첫 번째 INSERT 확인
        insert_call = cur.execute.call_args_list[1]
        args = insert_call[0][1]
        assert args[0] == "GEEKNEWS"
        assert args[1] == "LangChain"
        assert args[2] == 1  # rank
        assert args[3] == 47  # mention_count

    def test_saves_snapshot_for_hn(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.fetchall.return_value = [("React", 20)]

        sync._save_trend_snapshot(cur, "hn", top_n=10)

        assert cur.execute.call_count == 2  # SELECT + 1 INSERT
        insert_args = cur.execute.call_args_list[1][0][1]
        assert insert_args[0] == "HN"
        assert insert_args[1] == "React"

    def test_saves_snapshot_for_devto(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.fetchall.return_value = [("Python", 15)]

        sync._save_trend_snapshot(cur, "devto", top_n=10)

        insert_args = cur.execute.call_args_list[1][0][1]
        assert insert_args[0] == "DEVTO"

    def test_skips_unknown_source(self):
        sync = self._make_sync()
        cur = MagicMock()

        sync._save_trend_snapshot(cur, "unknown_source", top_n=20)

        cur.execute.assert_not_called()

    def test_skips_when_no_data(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.fetchall.return_value = []

        sync._save_trend_snapshot(cur, "geeknews", top_n=20)

        # SELECT만 실행, INSERT 없음
        assert cur.execute.call_count == 1

    def test_rank_ordering(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.fetchall.return_value = [
            ("Skill1", 100),
            ("Skill2", 80),
            ("Skill3", 50),
        ]

        sync._save_trend_snapshot(cur, "geeknews", top_n=20)

        # rank 값 확인 (1, 2, 3 순서)
        for i in range(3):
            insert_args = cur.execute.call_args_list[i + 1][0][1]
            assert insert_args[2] == i + 1  # rank

    def test_handles_db_error_gracefully(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.execute.side_effect = Exception("DB connection lost")

        # 예외가 발생해도 메서드 자체는 실패하지 않음
        sync._save_trend_snapshot(cur, "geeknews", top_n=20)

    def test_case_insensitive_source_name(self):
        sync = self._make_sync()
        cur = MagicMock()
        cur.fetchall.return_value = [("Go", 10)]

        sync._save_trend_snapshot(cur, "GeekNews", top_n=20)

        insert_args = cur.execute.call_args_list[1][0][1]
        assert insert_args[0] == "GEEKNEWS"
