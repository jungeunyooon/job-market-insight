from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

from crawlers.base import RawJobPosting
from crawlers.tech_blog import BlogPost
from crawlers.trend.base import TrendPost
from nlp.skill_matcher import SkillMatcher

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
SKILLS_SEED_PATH = ROOT_DIR / "data" / "skills_seed.json"
COMPANIES_SEED_PATH = ROOT_DIR / "data" / "companies_seed.json"


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

    def close(self) -> None:
        self._conn.close()

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
                cur.execute(
                    """
                    INSERT INTO skill (name, name_ko, category, aliases, source_scope)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET name_ko = COALESCE(skill.name_ko, EXCLUDED.name_ko),
                        category = COALESCE(skill.category, EXCLUDED.category),
                        aliases = CASE WHEN jsonb_array_length(skill.aliases) > 0 THEN skill.aliases ELSE EXCLUDED.aliases END,
                        source_scope = skill.source_scope
                    """,
                    (
                        name,
                        skill.get("name_ko"),
                        str(skill.get("category", "unknown")),
                        Json(aliases),
                        str(skill.get("source_scope", "BOTH")),
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

    def sync_job_postings(self, postings: list[RawJobPosting]) -> SyncStats:
        stats = SyncStats(crawled=len(postings))
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
                    for skill_name in skills:
                        skill_id = self._ensure_skill(cur, skill_name)
                        cur.execute(
                            """
                            INSERT INTO posting_skill (posting_id, skill_id, is_required, is_preferred, created_at)
                            VALUES (%s, %s, false, false, NOW())
                            ON CONFLICT (posting_id, skill_id) DO NOTHING
                            """,
                            (posting_id, skill_id),
                        )
                except Exception:
                    stats.failed += 1
                    logger.exception("Failed to sync job posting: %s / %s", post.company_name, post.title)

            self._conn.commit()
        return stats

    def sync_blog_posts(self, posts: list[BlogPost]) -> SyncStats:
        stats = SyncStats(crawled=len(posts))
        with self._conn.cursor() as cur:
            for post in posts:
                try:
                    company_id = self._upsert_company(cur, post.company_name)
                    blog_id, inserted = self._upsert_blog_post(cur, company_id, post)
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
                except Exception:
                    stats.failed += 1
                    logger.exception("Failed to sync blog post: %s", post.url)

            self._conn.commit()
        return stats

    def sync_trend_posts(self, posts: list[TrendPost]) -> SyncStats:
        stats = SyncStats(crawled=len(posts))
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
                except Exception:
                    stats.failed += 1
                    logger.exception("Failed to sync trend post: %s", post.external_id)

            self._conn.commit()
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
        text = f"{title}\n{description}".lower()
        product_keywords = ["product", "pm", "기획", "프로덕트"]
        fde_keywords = ["frontend", "front-end", "react", "vue", "ui", "ux", "프론트"]

        if any(k in text for k in product_keywords):
            return "PRODUCT"
        if any(k in text for k in fde_keywords):
            return "FDE"
        return "BACKEND"

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

    def _upsert_blog_post(self, cur, company_id: int, post: BlogPost) -> tuple[int, bool]:
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
                published_at, published_year, crawled_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
            """,
            (
                company_id,
                post.title,
                url,
                post.content_raw,
                post.content_raw,
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

    def _extract_job_skills(self, post: RawJobPosting) -> list[str]:
        extracted: set[str] = set()
        for tag in post.tags:
            cleaned = str(tag).strip()
            if cleaned:
                extracted.add(cleaned)

        text = f"{post.title}\n{post.description_raw}"
        for matched in self._skill_matcher.match(text, scope="JOB_POSTING"):
            extracted.add(matched.skill_name)

        return sorted(extracted)
