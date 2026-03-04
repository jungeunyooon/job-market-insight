"""DevPulse batch entry point.

Usage:
    python main.py crawl-jobs     # Crawl job postings
    python main.py crawl-blogs    # Crawl tech blogs
    python main.py crawl-trends   # Crawl trend news
    python main.py extract-skills # Extract skills from postings
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def cmd_crawl_jobs() -> None:
    from crawlers.wanted import WantedAPICrawler
    from crawlers.jumpit import JumpitCrawler
    from crawlers.greenhouse import GreenhouseCrawler

    crawlers = [
        ("WantedAPICrawler", WantedAPICrawler()),
        ("JumpitCrawler", JumpitCrawler()),
        ("GreenhouseCrawler", GreenhouseCrawler()),
    ]

    total = 0
    results: dict[str, int] = {}

    for name, crawler in crawlers:
        try:
            postings = crawler.crawl()
            count = len(postings)
            results[name] = count
            total += count
            print(f"  {name}: {count} postings")
        except Exception as exc:
            results[name] = 0
            print(f"  {name}: ERROR - {exc}")
            logger.error(f"{name} failed: {exc}", exc_info=True)

    print(f"\n[crawl-jobs] Summary: {total} total postings from {len(crawlers)} crawlers")
    for name, count in results.items():
        print(f"  - {name}: {count}")


def cmd_crawl_blogs() -> None:
    from crawlers.tech_blog import TechBlogCrawler

    crawlers = [
        ("TechBlogCrawler", TechBlogCrawler()),
    ]

    total = 0
    results: dict[str, int] = {}

    for name, crawler in crawlers:
        try:
            posts = crawler.crawl()
            count = len(posts)
            results[name] = count
            total += count
            print(f"  {name}: {count} posts")
        except Exception as exc:
            results[name] = 0
            print(f"  {name}: ERROR - {exc}")
            logger.error(f"{name} failed: {exc}", exc_info=True)

    print(f"\n[crawl-blogs] Summary: {total} total posts from {len(crawlers)} crawlers")
    for name, count in results.items():
        print(f"  - {name}: {count}")


def cmd_crawl_trends() -> None:
    from crawlers.trend.geeknews import GeekNewsCrawler
    from crawlers.trend.hackernews import HackerNewsCrawler
    from crawlers.trend.devto import DevToCrawler

    crawlers = [
        ("GeekNewsCrawler", GeekNewsCrawler()),
        ("HackerNewsCrawler", HackerNewsCrawler()),
        ("DevToCrawler", DevToCrawler()),
    ]

    total = 0
    results: dict[str, int] = {}

    for name, crawler in crawlers:
        try:
            posts = crawler.crawl()
            count = len(posts)
            results[name] = count
            total += count
            print(f"  {name}: {count} posts")
        except Exception as exc:
            results[name] = 0
            print(f"  {name}: ERROR - {exc}")
            logger.error(f"{name} failed: {exc}", exc_info=True)

    print(f"\n[crawl-trends] Summary: {total} total posts from {len(crawlers)} crawlers")
    for name, count in results.items():
        print(f"  - {name}: {count}")


def cmd_extract_skills() -> None:
    # Requires DB integration: load postings from DB, run SkillMatcher, persist results.
    # SkillMatcher usage: matcher = SkillMatcher(skills_path); matched = matcher.match(text)
    print("[extract-skills] Skill extraction requires DB integration (not yet implemented).")
    print("  Planned: load postings from DB -> SkillMatcher.match(description) -> persist MatchedSkill results")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print("Commands: crawl-jobs, crawl-blogs, crawl-trends, extract-skills")
        sys.exit(1)

    command = sys.argv[1]

    if command == "crawl-jobs":
        cmd_crawl_jobs()
    elif command == "crawl-blogs":
        cmd_crawl_blogs()
    elif command == "crawl-trends":
        cmd_crawl_trends()
    elif command == "extract-skills":
        cmd_extract_skills()
    else:
        print(f"Unknown command: {command}")
        print("Commands: crawl-jobs, crawl-blogs, crawl-trends, extract-skills")
        sys.exit(1)


if __name__ == "__main__":
    main()
