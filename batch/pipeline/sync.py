from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import psycopg2
from psycopg2.extras import Json

from crawlers.base import RawJobPosting
from crawlers.tech_blog import BlogPost
from crawlers.trend.base import TrendPost
from nlp.llm_summarizer import llm_summarize
from nlp.skill_matcher import SkillMatcher
from nlp.summarizer import extractive_summary

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
SKILLS_SEED_PATH = ROOT_DIR / "data" / "skills_seed.json"
COMPANIES_SEED_PATH = ROOT_DIR / "data" / "companies_seed.json"

CrawlStatusLiteral = Literal["SUCCESS", "PARTIAL", "FAILED"]


@dataclass
class SyncStats:
    crawled: int = 0
    inserted: int = 0
    updated: int = 0
    failed: int = 0


class DevPulseSync:
    def __init__(self) -> None:
        self._conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "devpulse"),
            user=os.getenv("DB_USER", "devpulse"),
            password=os.getenv("DB_PASSWORD", "devpulse1234"),
        )
        self._conn.autocommit = False

        self._seed_skills = self._load_json(SKILLS_SEED_PATH)
        self._seed_companies = self._load_json(COMPANIES_SEED_PATH)
        self._alias_to_company = self._build_company_alias_map(self._seed_companies)

        self._skill_matcher = SkillMatcher(self._seed_skills)
        self._skill_keywords: dict[str, list[str]] = {
            str(s.get("name", "")).strip().lower(): [str(k).strip() for k in s.get("keywords", []) if str(k).strip()]
            for s in self._seed_skills
            if str(s.get("name", "")).strip()
        }

    def close(self) -> None:
        self._conn.close()

    def log_crawl_execution(
        self,
        source_type: str,
        source_name: str,
        status: CrawlStatusLiteral,
        stats: SyncStats,
        started_at: datetime,
        finished_at: datetime,
        error_message: str | None = None,
    ) -> None:
        """crawl_log 테이블에 크롤링 실행 결과를 기록한다."""
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        items_duplicate = stats.crawled - stats.inserted - stats.updated - stats.failed
        if items_duplicate < 0:
            items_duplicate = 0
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO crawl_log (
                        source_type, source_name, status,
                        items_collected, items_new, items_duplicate,
                        error_message, duration_ms, started_at, finished_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        source_type,
                        source_name,
                        status,
                        stats.crawled,
                        stats.inserted,
                        items_duplicate,
                        error_message,
                        duration_ms,
                        started_at,
                        finished_at,
                    ),
                )
                self._conn.commit()
        except Exception:
            logger.exception(
                "crawl_log 기록 실패: source_type=%s source_name=%s", source_type, source_name
            )

    def _load_json(self, path: Path) -> list[dict]:
        if not path.exists():
            logger.warning("Seed file not found: %s", path)
            return []
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _build_company_alias_map(self, seeds: list[dict]) -> dict[str, dict]:
        mapping: dict[str, dict] = {}
        for company in seeds:
            canonical = company.get("name", "").strip()
            if not canonical:
                continue
            mapping[canonical.lower()] = company
            for alias in company.get("aliases", []):
                alias_norm = str(alias).strip().lower()
                if alias_norm:
                    mapping[alias_norm] = company
        return mapping

    def seed_reference_data(self) -> None:
        with self._conn.cursor() as cur:
            for skill in self._seed_skills:
                name = str(skill.get("name", "")).strip()
                if not name:
                    continue
                aliases = [str(a).strip() for a in skill.get("aliases", []) if str(a).strip()]
                keywords = [str(k).strip() for k in skill.get("keywords", []) if str(k).strip()]
                cur.execute(
                    """
                    INSERT INTO skill (name, name_ko, category, aliases, source_scope, keywords)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET name_ko = COALESCE(skill.name_ko, EXCLUDED.name_ko),
                        category = COALESCE(skill.category, EXCLUDED.category),
                        aliases = CASE WHEN jsonb_array_length(skill.aliases) > 0 THEN skill.aliases ELSE EXCLUDED.aliases END,
                        source_scope = skill.source_scope,
                        keywords = CASE WHEN jsonb_array_length(EXCLUDED.keywords) > 0 THEN EXCLUDED.keywords ELSE skill.keywords END
                    """,
                    (
                        name,
                        skill.get("name_ko"),
                        str(skill.get("category", "unknown")),
                        Json(aliases),
                        str(skill.get("source_scope", "BOTH")),
                        Json(keywords),
                    ),
                )

            for company in self._seed_companies:
                name = str(company.get("name", "")).strip()
                if not name:
                    continue
                aliases = [str(a).strip() for a in company.get("aliases", []) if str(a).strip()]
                tags = [str(t).strip() for t in company.get("tags", []) if str(t).strip()]
                cur.execute(
                    """
                    INSERT INTO company (
                        name, name_en, category, tags, aliases,
                        careers_url, tech_blog_url, tech_blog_type, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    ON CONFLICT (name) DO UPDATE
                    SET updated_at = NOW(),
                        name_en = COALESCE(company.name_en, EXCLUDED.name_en),
                        careers_url = COALESCE(company.careers_url, EXCLUDED.careers_url),
                        tech_blog_url = COALESCE(company.tech_blog_url, EXCLUDED.tech_blog_url),
                        tech_blog_type = COALESCE(company.tech_blog_type, EXCLUDED.tech_blog_type),
                        category = company.category
                    """,
                    (
                        name,
                        company.get("name_en"),
                        str(company.get("category", "UNCATEGORIZED")),
                        Json(tags),
                        Json(aliases),
                        company.get("careers_url"),
                        company.get("tech_blog_url"),
                        company.get("tech_blog_type"),
                    ),
                )

            self._conn.commit()

    def sync_job_postings(self, postings: list[RawJobPosting], source_name: str = "job_postings") -> SyncStats:
        started_at = datetime.now(timezone.utc)
        stats = SyncStats(crawled=len(postings))
        error_message: str | None = None
        with self._conn.cursor() as cur:
            for post in postings:
                try:
                    company_id = self._upsert_company(cur, post.company_name)
                    posting_id, inserted = self._upsert_job_posting(cur, company_id, post)
                    if inserted:
                        stats.inserted += 1
                    else:
                        stats.updated += 1

                    skills = self._extract_job_skills(post)
                    for skill_info in skills:
                        skill_id = self._ensure_skill(cur, skill_info["name"])
                        matched_keywords = self._extract_matched_keywords(skill_info["name"], post.description_raw)
                        cur.execute(
                            """
                            INSERT INTO posting_skill (posting_id, skill_id, is_required, is_preferred, matched_keywords, created_at)
                            VALUES (%s, %s, %s, %s, %s, NOW())
                            ON CONFLICT (posting_id, skill_id) DO UPDATE SET matched_keywords = EXCLUDED.matched_keywords
                            """,
                            (posting_id, skill_id, skill_info["is_required"], skill_info["is_preferred"], Json(matched_keywords)),
                        )
                except Exception as exc:
                    stats.failed += 1
                    error_message = str(exc)
                    logger.exception("Failed to sync job posting: %s / %s", post.company_name, post.title)

            self._conn.commit()

        finished_at = datetime.now(timezone.utc)
        status: CrawlStatusLiteral = "SUCCESS" if stats.failed == 0 else ("PARTIAL" if stats.inserted + stats.updated > 0 else "FAILED")
        self.log_crawl_execution("JOB_POSTING", source_name, status, stats, started_at, finished_at, error_message)
        return stats

    def sync_blog_posts(self, posts: list[BlogPost], source_name: str = "tech_blog") -> SyncStats:
        started_at = datetime.now(timezone.utc)
        stats = SyncStats(crawled=len(posts))
        error_message: str | None = None
        with self._conn.cursor() as cur:
            for post in posts:
                try:
                    company_id = self._upsert_company(cur, post.company_name)
                    summary = llm_summarize(post.content_raw) or extractive_summary(post.content_raw, max_sentences=3)
                    blog_id, inserted = self._upsert_blog_post(cur, company_id, post, summary=summary)
                    if inserted:
                        stats.inserted += 1
                    else:
                        stats.updated += 1

                    text = f"{post.title}\n{post.content_raw}"
                    matched = self._skill_matcher.match(text, scope="BOTH")
                    for m in matched:
                        skill_id = self._ensure_skill(cur, m.skill_name)
                        cur.execute(
                            """
                            INSERT INTO blog_skill (blog_post_id, skill_id, mention_count, created_at)
                            VALUES (%s, %s, 1, NOW())
                            ON CONFLICT (blog_post_id, skill_id)
                            DO UPDATE SET mention_count = GREATEST(blog_skill.mention_count, EXCLUDED.mention_count)
                            """,
                            (blog_id, skill_id),
                        )
                except Exception as exc:
                    stats.failed += 1
                    error_message = str(exc)
                    logger.exception("Failed to sync blog post: %s", post.url)

            self._conn.commit()

        finished_at = datetime.now(timezone.utc)
        status: CrawlStatusLiteral = "SUCCESS" if stats.failed == 0 else ("PARTIAL" if stats.inserted + stats.updated > 0 else "FAILED")
        self.log_crawl_execution("BLOG", source_name, status, stats, started_at, finished_at, error_message)
        return stats

    def sync_trend_posts(self, posts: list[TrendPost], source_name: str = "trend") -> SyncStats:
        started_at = datetime.now(timezone.utc)
        stats = SyncStats(crawled=len(posts))
        error_message: str | None = None
        with self._conn.cursor() as cur:
            for post in posts:
                try:
                    trend_id, inserted = self._upsert_trend_post(cur, post)
                    if inserted:
                        stats.inserted += 1
                    else:
                        stats.updated += 1

                    matched = self._skill_matcher.match(post.title, scope="TREND")
                    for m in matched:
                        skill_id = self._ensure_skill(cur, m.skill_name)
                        cur.execute(
                            """
                            INSERT INTO trend_skill (trend_post_id, skill_id, created_at)
                            VALUES (%s, %s, NOW())
                            ON CONFLICT (trend_post_id, skill_id) DO NOTHING
                            """,
                            (trend_id, skill_id),
                        )
                except Exception as exc:
                    stats.failed += 1
                    error_message = str(exc)
                    logger.exception("Failed to sync trend post: %s", post.external_id)

            self._conn.commit()

        finished_at = datetime.now(timezone.utc)
        status: CrawlStatusLiteral = "SUCCESS" if stats.failed == 0 else ("PARTIAL" if stats.inserted + stats.updated > 0 else "FAILED")
        self.log_crawl_execution("TREND", source_name, status, stats, started_at, finished_at, error_message)
        return stats

    def _canonical_company_seed(self, raw_name: str) -> dict | None:
        key = raw_name.strip().lower()
        return self._alias_to_company.get(key)

    def _upsert_company(self, cur, raw_name: str) -> int:
        company_seed = self._canonical_company_seed(raw_name)
        if company_seed:
            name = company_seed.get("name", raw_name).strip()
            category = company_seed.get("category", "UNCATEGORIZED")
            aliases = company_seed.get("aliases", [])
            tags = company_seed.get("tags", [])
        else:
            name = raw_name.strip() or "Unknown"
            category = "UNCATEGORIZED"
            aliases = [name]
            tags = []

        cur.execute(
            """
            INSERT INTO company (name, category, tags, aliases, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (name) DO UPDATE SET updated_at = NOW()
            RETURNING id
            """,
            (name, category, Json(tags), Json(aliases)),
        )
        return int(cur.fetchone()[0])

    def _normalize_title(self, title: str) -> str:
        return re.sub(r"\s+", " ", (title or "").strip().lower())

    def _infer_position_type(self, title: str, description: str) -> str:
        title_lower = title.lower()

        # Title-based classification (high confidence)
        backend_title = ["backend", "back-end", "back end", "서버", "백엔드", "server", "spring", "java developer", "python developer", "go developer"]
        fde_title = ["frontend", "front-end", "front end", "프론트엔드", "프론트", "react developer", "vue developer", "ui developer", "ux engineer"]
        product_title = ["product manager", "product owner", "기획자", "프로덕트", "pm"]

        if any(k in title_lower for k in backend_title):
            return "BACKEND"
        if any(k in title_lower for k in fde_title):
            return "FDE"
        if any(k in title_lower for k in product_title):
            return "PRODUCT"

        # Fallback: check description but with stricter matching
        desc_lower = description.lower()
        backend_desc = ["backend", "back-end", "서버 개발", "백엔드", "spring boot", "api 개발"]
        fde_desc = ["frontend", "front-end", "프론트엔드", "react 개발", "vue 개발", "ui/ux"]

        if any(k in desc_lower for k in backend_desc):
            return "BACKEND"
        if any(k in desc_lower for k in fde_desc):
            return "FDE"

        return "BACKEND"  # default to backend

    def _upsert_job_posting(self, cur, company_id: int, post: RawJobPosting) -> tuple[int, bool]:
        title = (post.title or "").strip() or "(untitled)"
        posted_at = post.posted_at or datetime.now(timezone.utc)
        position_type = self._infer_position_type(title, post.description_raw)
        title_normalized = self._normalize_title(title)
        source_platform = (post.source_platform or "unknown").strip().lower()
        source_url = (post.source_url or "").strip() or f"urn:generated:{company_id}:{title_normalized}"

        cur.execute(
            "SELECT id FROM job_posting WHERE source_platform = %s AND source_url = %s LIMIT 1",
            (source_platform, source_url),
        )
        row = cur.fetchone()
        if row:
            posting_id = int(row[0])
            cur.execute(
                """
                UPDATE job_posting
                SET company_id = %s,
                    title = %s,
                    title_normalized = %s,
                    position_type = %s,
                    experience_level = %s,
                    description_raw = %s,
                    description_cleaned = %s,
                    location = %s,
                    status = 'ACTIVE',
                    posted_at = %s,
                    last_seen_at = NOW(),
                    crawled_at = NOW()
                WHERE id = %s
                """,
                (
                    company_id,
                    title,
                    title_normalized,
                    position_type,
                    post.experience_level,
                    post.description_raw,
                    post.description_raw,
                    post.location,
                    posted_at,
                    posting_id,
                ),
            )
            return posting_id, False

        cur.execute(
            """
            INSERT INTO job_posting (
                company_id, title, title_normalized, position_type, experience_level,
                description_raw, description_cleaned, source_platform, source_url,
                salary_min, salary_max, location, status, posted_at,
                crawled_at, last_seen_at, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', %s, NOW(), NOW(), NOW())
            RETURNING id
            """,
            (
                company_id,
                title,
                title_normalized,
                position_type,
                post.experience_level,
                post.description_raw,
                post.description_raw,
                source_platform,
                source_url,
                post.salary_min,
                post.salary_max,
                post.location,
                posted_at,
            ),
        )
        return int(cur.fetchone()[0]), True

    def _upsert_blog_post(self, cur, company_id: int, post: BlogPost, summary: str = "") -> tuple[int, bool]:
        url = (post.url or "").strip()
        if not url:
            raise ValueError("blog post url is empty")

        cur.execute("SELECT id FROM tech_blog_post WHERE url = %s LIMIT 1", (url,))
        row = cur.fetchone()
        if row:
            blog_id = int(row[0])
            cur.execute(
                """
                UPDATE tech_blog_post
                SET company_id = %s,
                    title = %s,
                    content_raw = %s,
                    content_cleaned = %s,
                    summary = %s,
                    published_at = %s,
                    published_year = %s,
                    crawled_at = NOW()
                WHERE id = %s
                """,
                (
                    company_id,
                    post.title,
                    post.content_raw,
                    post.content_raw,
                    summary,
                    post.published_at,
                    post.published_year,
                    blog_id,
                ),
            )
            return blog_id, False

        cur.execute(
            """
            INSERT INTO tech_blog_post (
                company_id, title, url, content_raw, content_cleaned,
                summary, published_at, published_year, crawled_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
            """,
            (
                company_id,
                post.title,
                url,
                post.content_raw,
                post.content_raw,
                summary,
                post.published_at,
                post.published_year,
            ),
        )
        return int(cur.fetchone()[0]), True

    def _upsert_trend_post(self, cur, post: TrendPost) -> tuple[int, bool]:
        cur.execute(
            "SELECT id FROM trend_post WHERE source = %s AND external_id = %s LIMIT 1",
            (post.source, post.external_id),
        )
        row = cur.fetchone()
        if row:
            trend_id = int(row[0])
            cur.execute(
                """
                UPDATE trend_post
                SET title = %s,
                    url = %s,
                    score = %s,
                    comment_count = %s,
                    published_at = %s,
                    crawled_at = NOW()
                WHERE id = %s
                """,
                (
                    post.title,
                    post.url,
                    post.score,
                    post.comment_count,
                    post.published_at,
                    trend_id,
                ),
            )
            return trend_id, False

        cur.execute(
            """
            INSERT INTO trend_post (
                source, external_id, title, url, score, comment_count, published_at, crawled_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
            """,
            (
                post.source,
                post.external_id,
                post.title,
                post.url,
                post.score,
                post.comment_count,
                post.published_at,
            ),
        )
        return int(cur.fetchone()[0]), True

    def _ensure_skill(self, cur, skill_name: str) -> int:
        skill_name = skill_name.strip()
        if not skill_name:
            raise ValueError("skill name is empty")

        cur.execute(
            """
            INSERT INTO skill (name, category, aliases, source_scope)
            VALUES (%s, %s, %s, 'BOTH')
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (skill_name, "unknown", Json([skill_name])),
        )
        return int(cur.fetchone()[0])

    def _classify_skill_requirement(self, skill_name: str, description: str) -> tuple[bool, bool]:
        """스킬이 필수/우대 섹션 중 어디에 등장하는지 판단한다."""
        required_headers = ["자격요건", "필수", "요구사항", "필수 조건", "지원자격", "requirements", "required", "qualifications", "must have"]
        preferred_headers = ["우대", "우대사항", "우대 조건", "플러스", "preferred", "nice to have", "bonus", "plus"]

        # Split description into sections by common headers
        header_pattern = "|".join(re.escape(h) for h in required_headers + preferred_headers)
        sections = re.split(rf"({header_pattern})", description, flags=re.IGNORECASE)

        current_section: str | None = None
        skill_lower = skill_name.lower()

        for chunk in sections:
            chunk_lower = chunk.lower().strip()
            if any(chunk_lower == h.lower() for h in required_headers):
                current_section = "required"
            elif any(chunk_lower == h.lower() for h in preferred_headers):
                current_section = "preferred"
            elif skill_lower in chunk_lower:
                if current_section == "preferred":
                    return False, True
                else:
                    # required section or ambiguous → default to required
                    return True, False

        # skill found but no section detected → default to required
        if skill_lower in description.lower():
            return True, False

        return True, False

    def _extract_matched_keywords(self, skill_name: str, description: str) -> list[str]:
        """스킬의 세부 키워드 중 description에 등장하는 것을 반환한다."""
        keywords = self._skill_keywords.get(skill_name.strip().lower(), [])
        desc_lower = description.lower()
        return [kw for kw in keywords if kw.lower() in desc_lower]

    def _extract_job_skills(self, post: RawJobPosting) -> list[dict]:
        extracted: dict[str, dict] = {}
        for tag in post.tags:
            cleaned = str(tag).strip()
            if cleaned and cleaned not in extracted:
                is_required, is_preferred = self._classify_skill_requirement(cleaned, post.description_raw)
                extracted[cleaned] = {"name": cleaned, "is_required": is_required, "is_preferred": is_preferred}

        text = f"{post.title}\n{post.description_raw}"
        for matched in self._skill_matcher.match(text, scope="JOB_POSTING"):
            name = matched.skill_name
            if name not in extracted:
                is_required, is_preferred = self._classify_skill_requirement(name, post.description_raw)
                extracted[name] = {"name": name, "is_required": is_required, "is_preferred": is_preferred}

        return sorted(extracted.values(), key=lambda x: x["name"])
