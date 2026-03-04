"""DevPulse batch entry point.

Usage:
    python main.py crawl-jobs     # Crawl job postings
    python main.py crawl-blogs    # Crawl tech blogs
    python main.py crawl-trends   # Crawl trend news
    python main.py extract-skills # Extract skills from postings
"""

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print("Commands: crawl-jobs, crawl-blogs, crawl-trends, extract-skills")
        sys.exit(1)

    command = sys.argv[1]

    if command == "crawl-jobs":
        print("Job crawling not yet implemented (Phase 1)")
    elif command == "crawl-blogs":
        print("Blog crawling not yet implemented (Phase 2)")
    elif command == "crawl-trends":
        print("Trend crawling not yet implemented (Phase 2)")
    elif command == "extract-skills":
        print("Skill extraction not yet implemented (Phase 1)")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
