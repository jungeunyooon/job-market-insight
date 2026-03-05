"""DevPulse 배치 스케줄러.

컨테이너 내부에서 장기 실행되며 6시간마다 sync-all 파이프라인을 실행한다.

Usage:
    python scheduler.py            # 6시간 주기 (기본값)
    python scheduler.py --interval 2   # 2시간 주기 (테스트용)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone

import schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_sync_all() -> None:
    """sync-all 파이프라인을 실행하고 결과를 로그에 기록한다."""
    started = datetime.now(timezone.utc)
    logger.info("스케줄 실행 시작: sync-all (started_at=%s)", started.isoformat())
    try:
        # main.py의 cmd_sync_all을 직접 호출하여 코드 중복을 피한다
        from main import cmd_sync_all  # noqa: PLC0415

        cmd_sync_all()
        finished = datetime.now(timezone.utc)
        elapsed = (finished - started).total_seconds()
        logger.info("스케줄 실행 완료: sync-all (elapsed=%.1fs)", elapsed)
    except Exception:
        finished = datetime.now(timezone.utc)
        elapsed = (finished - started).total_seconds()
        logger.exception("스케줄 실행 실패: sync-all (elapsed=%.1fs)", elapsed)


def main() -> None:
    parser = argparse.ArgumentParser(description="DevPulse 배치 스케줄러")
    parser.add_argument(
        "--interval",
        type=int,
        default=6,
        metavar="HOURS",
        help="실행 주기 (시간 단위, 기본값: 6)",
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="시작 시 즉시 한 번 실행 후 스케줄 대기",
    )
    args = parser.parse_args()

    logger.info("DevPulse 스케줄러 시작: 매 %d시간마다 sync-all 실행", args.interval)

    schedule.every(args.interval).hours.do(run_sync_all)

    if args.run_now:
        logger.info("--run-now 플래그: 즉시 첫 실행")
        run_sync_all()

    logger.info("다음 실행 예정: %s", schedule.next_run())

    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 스케줄 확인


if __name__ == "__main__":
    main()
