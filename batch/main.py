"""DevPulse batch entry point.

Usage:
    python main.py crawl-jobs      # Crawl job postings only
    python main.py crawl-blogs     # Crawl tech blogs only
    python main.py crawl-trends    # Crawl trend news only
    python main.py sync-jobs       # Crawl + DB upsert (job postings)
    python main.py sync-blogs      # Crawl + DB upsert (tech blogs)
    python main.py sync-trends     # Crawl + DB upsert (trend posts)
    python main.py sync-all        # Run all sync pipelines
    python main.py extract-skills  # Reserved
"""

import logging
import sys
import time

from pipeline.sync import DevPulseSync, SyncStats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def run_job_crawlers() -> dict[str, list]:
    from crawlers.greenhouse import GreenhouseCrawler
    from crawlers.jumpit import JumpitCrawler
    from crawlers.superrookie import SuperRookieCrawler
    from crawlers.wanted import WantedAPICrawler

    crawlers = [
        ("WantedAPICrawler", WantedAPICrawler()),
        ("JumpitCrawler", JumpitCrawler()),
        ("GreenhouseCrawler", GreenhouseCrawler()),
        ("SuperRookieCrawler", SuperRookieCrawler()),
    ]

    results: dict[str, list] = {}
    for name, crawler in crawlers:
        try:
            postings = crawler.crawl()
            results[name] = postings
            print(f"  {name}: {len(postings)} postings")
        except Exception as exc:
            results[name] = []
            print(f"  {name}: ERROR - {exc}")
            logger.error("%s failed: %s", name, exc, exc_info=True)
    return results


def run_blog_crawlers() -> dict[str, list]:
    from crawlers.tech_blog import TechBlogCrawler

    crawlers = [("TechBlogCrawler", TechBlogCrawler())]

    results: dict[str, list] = {}
    for name, crawler in crawlers:
        try:
            posts = crawler.crawl()
            results[name] = posts
            print(f"  {name}: {len(posts)} posts")
        except Exception as exc:
            results[name] = []
            print(f"  {name}: ERROR - {exc}")
            logger.error("%s failed: %s", name, exc, exc_info=True)
    return results


def run_trend_crawlers() -> dict[str, list]:
    from crawlers.trend.devto import DevToCrawler
    from crawlers.trend.geeknews import GeekNewsCrawler
    from crawlers.trend.hackernews import HackerNewsCrawler

    crawlers = [
        ("GeekNewsCrawler", GeekNewsCrawler()),
        ("HackerNewsCrawler", HackerNewsCrawler()),
        ("DevToCrawler", DevToCrawler()),
    ]

    results: dict[str, list] = {}
    for name, crawler in crawlers:
        try:
            posts = crawler.crawl()
            results[name] = posts
            print(f"  {name}: {len(posts)} posts")
        except Exception as exc:
            results[name] = []
            print(f"  {name}: ERROR - {exc}")
            logger.error("%s failed: %s", name, exc, exc_info=True)
    return results


def cmd_crawl_jobs() -> None:
    results = run_job_crawlers()
    total = sum(len(items) for items in results.values())
    print(f"\n[crawl-jobs] Summary: {total} total postings from {len(results)} crawlers")
    for name, items in results.items():
        print(f"  - {name}: {len(items)}")


def cmd_crawl_blogs() -> None:
    results = run_blog_crawlers()
    total = sum(len(items) for items in results.values())
    print(f"\n[crawl-blogs] Summary: {total} total posts from {len(results)} crawlers")
    for name, items in results.items():
        print(f"  - {name}: {len(items)}")


def cmd_crawl_trends() -> None:
    results = run_trend_crawlers()
    total = sum(len(items) for items in results.values())
    print(f"\n[crawl-trends] Summary: {total} total posts from {len(results)} crawlers")
    for name, items in results.items():
        print(f"  - {name}: {len(items)}")


_RETRY_DELAYS = [2, 4]  # 지수 백오프: 1차 재시도 2초, 2차 재시도 4초


def _sync_with_retry(label: str, sync_fn, items: list, source_name: str) -> tuple[SyncStats, bool]:
    """단일 crawler 항목을 최대 2회 재시도하여 동기화한다. (pass=True, fail=False)"""
    last_exc: Exception | None = None
    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            stats = sync_fn(items, source_name=source_name)
            if attempt > 0:
                print(f"    {label}: 재시도 {attempt}회차 성공")
            return stats, True
        except Exception as exc:
            last_exc = exc
            if attempt < len(_RETRY_DELAYS):
                delay = _RETRY_DELAYS[attempt]
                print(f"    {label}: 오류 발생, {delay}초 후 재시도 ({attempt + 1}/{len(_RETRY_DELAYS)}) - {exc}")
                logger.warning("%s attempt %d failed: %s", label, attempt + 1, exc, exc_info=True)
                time.sleep(delay)
            else:
                print(f"    {label}: 최종 실패 - {exc}")
                logger.error("%s failed after %d attempts: %s", label, attempt + 1, exc, exc_info=True)

    empty = SyncStats()
    return empty, False


def _crawl_and_sync_with_retry(label: str, crawl_fn, sync_fn, source_name: str) -> tuple[SyncStats, bool]:
    """크롤링과 동기화를 묶어 최대 2회 재시도한다. 크롤 실패 시에도 재크롤한다. (pass=True, fail=False)"""
    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            items = crawl_fn()
            stats = sync_fn(items, source_name=source_name)
            if attempt > 0:
                print(f"    {label}: 재시도 {attempt}회차 성공")
            return stats, True
        except Exception as exc:
            if attempt < len(_RETRY_DELAYS):
                delay = _RETRY_DELAYS[attempt]
                print(f"    {label}: 오류 발생, {delay}초 후 재시도 ({attempt + 1}/{len(_RETRY_DELAYS)}) - {exc}")
                logger.warning("%s attempt %d failed: %s", label, attempt + 1, exc, exc_info=True)
                time.sleep(delay)
            else:
                print(f"    {label}: 최종 실패 - {exc}")
                logger.error("%s failed after %d attempts: %s", label, attempt + 1, exc, exc_info=True)

    return SyncStats(), False


def cmd_sync_jobs() -> None:
    results = run_job_crawlers()
    sync = DevPulseSync()
    try:
        sync.seed_reference_data()
        total = 0
        inserted = 0
        updated = 0
        failed = 0
        crawler_results: dict[str, bool] = {}

        for name, postings in results.items():
            stats, ok = _sync_with_retry(name, sync.sync_job_postings, postings, name)
            crawler_results[name] = ok
            total += stats.crawled
            inserted += stats.inserted
            updated += stats.updated
            failed += stats.failed
            status_str = "PASS" if ok else "FAIL"
            print(
                f"  [sync-jobs] {name} [{status_str}]: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )

        print(f"\n[sync-jobs] Summary: crawled={total}, inserted={inserted}, updated={updated}, failed={failed}")
        for name, ok in crawler_results.items():
            print(f"  - {name}: {'PASS' if ok else 'FAIL'}")
    finally:
        sync.close()


def cmd_sync_blogs() -> None:
    results = run_blog_crawlers()
    sync = DevPulseSync()
    try:
        sync.seed_reference_data()
        total = 0
        inserted = 0
        updated = 0
        failed = 0
        crawler_results: dict[str, bool] = {}

        for name, posts in results.items():
            stats, ok = _sync_with_retry(name, sync.sync_blog_posts, posts, name)
            crawler_results[name] = ok
            total += stats.crawled
            inserted += stats.inserted
            updated += stats.updated
            failed += stats.failed
            status_str = "PASS" if ok else "FAIL"
            print(
                f"  [sync-blogs] {name} [{status_str}]: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )

        print(f"\n[sync-blogs] Summary: crawled={total}, inserted={inserted}, updated={updated}, failed={failed}")
        for name, ok in crawler_results.items():
            print(f"  - {name}: {'PASS' if ok else 'FAIL'}")
    finally:
        sync.close()


def cmd_sync_trends() -> None:
    results = run_trend_crawlers()
    sync = DevPulseSync()
    try:
        sync.seed_reference_data()
        total = 0
        inserted = 0
        updated = 0
        failed = 0
        crawler_results: dict[str, bool] = {}

        for name, posts in results.items():
            stats, ok = _sync_with_retry(name, sync.sync_trend_posts, posts, name)
            crawler_results[name] = ok
            total += stats.crawled
            inserted += stats.inserted
            updated += stats.updated
            failed += stats.failed
            status_str = "PASS" if ok else "FAIL"
            print(
                f"  [sync-trends] {name} [{status_str}]: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )

        print(f"\n[sync-trends] Summary: crawled={total}, inserted={inserted}, updated={updated}, failed={failed}")
        for name, ok in crawler_results.items():
            print(f"  - {name}: {'PASS' if ok else 'FAIL'}")
    finally:
        sync.close()


def cmd_sync_all() -> None:
    from crawlers.greenhouse import GreenhouseCrawler
    from crawlers.jumpit import JumpitCrawler
    from crawlers.superrookie import SuperRookieCrawler
    from crawlers.tech_blog import TechBlogCrawler
    from crawlers.trend.devto import DevToCrawler
    from crawlers.trend.geeknews import GeekNewsCrawler
    from crawlers.trend.hackernews import HackerNewsCrawler
    from crawlers.wanted import WantedAPICrawler

    sync = DevPulseSync()
    try:
        sync.seed_reference_data()

        grand_total = 0
        grand_inserted = 0
        grand_updated = 0
        grand_failed = 0
        all_results: dict[str, bool] = {}

        # --- Step 1/3: jobs ---
        print("[sync-all] Step 1/3: jobs")
        job_crawlers = [
            ("WantedAPICrawler", WantedAPICrawler()),
            ("JumpitCrawler", JumpitCrawler()),
            ("GreenhouseCrawler", GreenhouseCrawler()),
            ("SuperRookieCrawler", SuperRookieCrawler()),
        ]
        job_total = job_inserted = job_updated = job_failed = 0
        for name, crawler in job_crawlers:
            stats, ok = _crawl_and_sync_with_retry(name, crawler.crawl, sync.sync_job_postings, name)
            all_results[name] = ok
            job_total += stats.crawled
            job_inserted += stats.inserted
            job_updated += stats.updated
            job_failed += stats.failed
            status_str = "PASS" if ok else "FAIL"
            print(
                f"  [sync-all/jobs] {name} [{status_str}]: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )
        print(f"\n[sync-all/jobs] Summary: crawled={job_total}, inserted={job_inserted}, updated={job_updated}, failed={job_failed}")
        grand_total += job_total
        grand_inserted += job_inserted
        grand_updated += job_updated
        grand_failed += job_failed

        # --- Step 2/3: blogs ---
        print("\n[sync-all] Step 2/3: blogs")
        blog_crawlers = [
            ("TechBlogCrawler", TechBlogCrawler()),
        ]
        blog_total = blog_inserted = blog_updated = blog_failed = 0
        for name, crawler in blog_crawlers:
            stats, ok = _crawl_and_sync_with_retry(name, crawler.crawl, sync.sync_blog_posts, name)
            all_results[name] = ok
            blog_total += stats.crawled
            blog_inserted += stats.inserted
            blog_updated += stats.updated
            blog_failed += stats.failed
            status_str = "PASS" if ok else "FAIL"
            print(
                f"  [sync-all/blogs] {name} [{status_str}]: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )
        print(f"\n[sync-all/blogs] Summary: crawled={blog_total}, inserted={blog_inserted}, updated={blog_updated}, failed={blog_failed}")
        grand_total += blog_total
        grand_inserted += blog_inserted
        grand_updated += blog_updated
        grand_failed += blog_failed

        # --- Step 3/3: trends ---
        print("\n[sync-all] Step 3/3: trends")
        trend_crawlers = [
            ("GeekNewsCrawler", GeekNewsCrawler()),
            ("HackerNewsCrawler", HackerNewsCrawler()),
            ("DevToCrawler", DevToCrawler()),
        ]
        trend_total = trend_inserted = trend_updated = trend_failed = 0
        for name, crawler in trend_crawlers:
            stats, ok = _crawl_and_sync_with_retry(name, crawler.crawl, sync.sync_trend_posts, name)
            all_results[name] = ok
            trend_total += stats.crawled
            trend_inserted += stats.inserted
            trend_updated += stats.updated
            trend_failed += stats.failed
            status_str = "PASS" if ok else "FAIL"
            print(
                f"  [sync-all/trends] {name} [{status_str}]: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )
        print(f"\n[sync-all/trends] Summary: crawled={trend_total}, inserted={trend_inserted}, updated={trend_updated}, failed={trend_failed}")
        grand_total += trend_total
        grand_inserted += trend_inserted
        grand_updated += trend_updated
        grand_failed += trend_failed

        print(f"\n[sync-all] Grand Total: crawled={grand_total}, inserted={grand_inserted}, updated={grand_updated}, failed={grand_failed}")
        for name, ok in all_results.items():
            print(f"  - {name}: {'PASS' if ok else 'FAIL'}")
    finally:
        sync.close()


def cmd_extract_skills() -> None:
    print("[extract-skills] integrated into sync commands via SkillMatcher")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print(
            "Commands: crawl-jobs, crawl-blogs, crawl-trends, "
            "sync-jobs, sync-blogs, sync-trends, sync-all, extract-skills"
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "crawl-jobs":
        cmd_crawl_jobs()
    elif command == "crawl-blogs":
        cmd_crawl_blogs()
    elif command == "crawl-trends":
        cmd_crawl_trends()
    elif command == "sync-jobs":
        cmd_sync_jobs()
    elif command == "sync-blogs":
        cmd_sync_blogs()
    elif command == "sync-trends":
        cmd_sync_trends()
    elif command == "sync-all":
        cmd_sync_all()
    elif command == "extract-skills":
        cmd_extract_skills()
    else:
        print(f"Unknown command: {command}")
        print(
            "Commands: crawl-jobs, crawl-blogs, crawl-trends, "
            "sync-jobs, sync-blogs, sync-trends, sync-all, extract-skills"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
