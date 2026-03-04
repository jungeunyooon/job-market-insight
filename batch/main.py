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

from pipeline.sync import DevPulseSync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def run_job_crawlers() -> dict[str, list]:
    from crawlers.greenhouse import GreenhouseCrawler
    from crawlers.jumpit import JumpitCrawler
    from crawlers.wanted import WantedAPICrawler

    crawlers = [
        ("WantedAPICrawler", WantedAPICrawler()),
        ("JumpitCrawler", JumpitCrawler()),
        ("GreenhouseCrawler", GreenhouseCrawler()),
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


def cmd_sync_jobs() -> None:
    results = run_job_crawlers()
    sync = DevPulseSync()
    try:
        sync.seed_reference_data()
        total = 0
        inserted = 0
        updated = 0
        failed = 0

        for name, postings in results.items():
            stats = sync.sync_job_postings(postings)
            total += stats.crawled
            inserted += stats.inserted
            updated += stats.updated
            failed += stats.failed
            print(
                f"  [sync-jobs] {name}: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )

        print(
            f"\n[sync-jobs] Summary: crawled={total}, inserted={inserted}, "
            f"updated={updated}, failed={failed}"
        )
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

        for name, posts in results.items():
            stats = sync.sync_blog_posts(posts)
            total += stats.crawled
            inserted += stats.inserted
            updated += stats.updated
            failed += stats.failed
            print(
                f"  [sync-blogs] {name}: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )

        print(
            f"\n[sync-blogs] Summary: crawled={total}, inserted={inserted}, "
            f"updated={updated}, failed={failed}"
        )
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

        for name, posts in results.items():
            stats = sync.sync_trend_posts(posts)
            total += stats.crawled
            inserted += stats.inserted
            updated += stats.updated
            failed += stats.failed
            print(
                f"  [sync-trends] {name}: crawled={stats.crawled}, "
                f"inserted={stats.inserted}, updated={stats.updated}, failed={stats.failed}"
            )

        print(
            f"\n[sync-trends] Summary: crawled={total}, inserted={inserted}, "
            f"updated={updated}, failed={failed}"
        )
    finally:
        sync.close()


def cmd_sync_all() -> None:
    print("[sync-all] Step 1/3: jobs")
    cmd_sync_jobs()
    print("[sync-all] Step 2/3: blogs")
    cmd_sync_blogs()
    print("[sync-all] Step 3/3: trends")
    cmd_sync_trends()


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
