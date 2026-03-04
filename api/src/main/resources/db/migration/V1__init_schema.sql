-- DevPulse Initial Schema
-- Based on PRD v3.0 Section 5.1 ERD

-- =============================================
-- ENUM Types
-- =============================================

CREATE TYPE company_category AS ENUM (
    'BIGTECH', 'BIGTECH_SUB', 'UNICORN', 'STARTUP',
    'SI', 'MID', 'FINANCE', 'UNCATEGORIZED'
);

CREATE TYPE position_type AS ENUM ('BACKEND', 'PRODUCT', 'FDE');

CREATE TYPE posting_status AS ENUM ('ACTIVE', 'CLOSED', 'EXPIRED', 'ARCHIVED');

CREATE TYPE skill_source_scope AS ENUM ('JOB_POSTING', 'TREND', 'BOTH');

CREATE TYPE trend_source AS ENUM ('GEEKNEWS', 'HN', 'DEVTO');

CREATE TYPE tech_blog_type AS ENUM ('rss', 'html', 'medium');

CREATE TYPE unmatched_status AS ENUM ('PENDING', 'RESOLVED', 'IGNORED');

CREATE TYPE crawl_status AS ENUM ('SUCCESS', 'PARTIAL', 'FAILED');

-- =============================================
-- Tables
-- =============================================

-- 회사
CREATE TABLE company (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    name_en         VARCHAR(200),
    category        company_category NOT NULL DEFAULT 'UNCATEGORIZED',
    tags            JSONB DEFAULT '[]',
    aliases         JSONB DEFAULT '[]',
    careers_url     VARCHAR(500),
    tech_blog_url   VARCHAR(500),
    tech_blog_type  tech_blog_type,
    employee_count_range VARCHAR(50),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_company_name ON company (name);
CREATE INDEX idx_company_category ON company (category);

-- 채용 공고 (영구 보관)
CREATE TABLE job_posting (
    id                  BIGSERIAL PRIMARY KEY,
    company_id          BIGINT NOT NULL REFERENCES company(id),
    title               VARCHAR(500) NOT NULL,
    title_normalized    VARCHAR(500),
    position_type       position_type,
    experience_level    VARCHAR(100),
    description_raw     TEXT,
    description_cleaned TEXT,
    source_platform     VARCHAR(50) NOT NULL,
    source_url          VARCHAR(1000) NOT NULL,
    salary_min          INTEGER,
    salary_max          INTEGER,
    location            VARCHAR(200),
    status              posting_status NOT NULL DEFAULT 'ACTIVE',
    closed_at           TIMESTAMP,
    posted_at           TIMESTAMP,
    crawled_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    last_seen_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_posting_company ON job_posting (company_id);
CREATE INDEX idx_posting_position ON job_posting (position_type);
CREATE INDEX idx_posting_status ON job_posting (status);
CREATE INDEX idx_posting_posted_at ON job_posting (posted_at);
CREATE INDEX idx_posting_source ON job_posting (source_platform);
CREATE UNIQUE INDEX idx_posting_dedup ON job_posting (company_id, title_normalized, posted_at);

-- 기술 사전
CREATE TABLE skill (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    name_ko         VARCHAR(100),
    category        VARCHAR(50) NOT NULL,
    aliases         JSONB DEFAULT '[]',
    source_scope    skill_source_scope NOT NULL DEFAULT 'BOTH',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_skill_name ON skill (name);
CREATE INDEX idx_skill_category ON skill (category);
CREATE INDEX idx_skill_scope ON skill (source_scope);

-- 공고-스킬 매핑
CREATE TABLE posting_skill (
    id              BIGSERIAL PRIMARY KEY,
    posting_id      BIGINT NOT NULL REFERENCES job_posting(id),
    skill_id        BIGINT NOT NULL REFERENCES skill(id),
    is_required     BOOLEAN DEFAULT FALSE,
    is_preferred    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ps_posting ON posting_skill (posting_id);
CREATE INDEX idx_ps_skill ON posting_skill (skill_id);
CREATE UNIQUE INDEX idx_ps_dedup ON posting_skill (posting_id, skill_id);

-- 테크 블로그 글
CREATE TABLE tech_blog_post (
    id              BIGSERIAL PRIMARY KEY,
    company_id      BIGINT NOT NULL REFERENCES company(id),
    title           VARCHAR(500) NOT NULL,
    url             VARCHAR(1000) NOT NULL,
    content_raw     TEXT,
    content_cleaned TEXT,
    summary         TEXT,
    topics          JSONB DEFAULT '[]',
    published_at    TIMESTAMP,
    published_year  INTEGER,
    crawled_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_blog_company ON tech_blog_post (company_id);
CREATE INDEX idx_blog_year ON tech_blog_post (published_year);
CREATE UNIQUE INDEX idx_blog_url ON tech_blog_post (url);

-- 블로그-스킬 매핑
CREATE TABLE blog_skill (
    id              BIGSERIAL PRIMARY KEY,
    blog_post_id    BIGINT NOT NULL REFERENCES tech_blog_post(id),
    skill_id        BIGINT NOT NULL REFERENCES skill(id),
    mention_count   INTEGER DEFAULT 1,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bs_blog ON blog_skill (blog_post_id);
CREATE INDEX idx_bs_skill ON blog_skill (skill_id);
CREATE UNIQUE INDEX idx_bs_dedup ON blog_skill (blog_post_id, skill_id);

-- 트렌드 뉴스 포스트
CREATE TABLE trend_post (
    id              BIGSERIAL PRIMARY KEY,
    source          trend_source NOT NULL,
    external_id     VARCHAR(200) NOT NULL,
    title           VARCHAR(500) NOT NULL,
    url             VARCHAR(1000),
    score           INTEGER DEFAULT 0,
    comment_count   INTEGER DEFAULT 0,
    published_at    TIMESTAMP,
    crawled_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_trend_source_ext ON trend_post (source, external_id);
CREATE INDEX idx_trend_published ON trend_post (published_at);

-- 트렌드-스킬 매핑
CREATE TABLE trend_skill (
    id              BIGSERIAL PRIMARY KEY,
    trend_post_id   BIGINT NOT NULL REFERENCES trend_post(id),
    skill_id        BIGINT NOT NULL REFERENCES skill(id),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ts_trend ON trend_skill (trend_post_id);
CREATE INDEX idx_ts_skill ON trend_skill (skill_id);
CREATE UNIQUE INDEX idx_ts_dedup ON trend_skill (trend_post_id, skill_id);

-- 미매칭 회사
CREATE TABLE unmatched_company (
    id                  BIGSERIAL PRIMARY KEY,
    raw_name            VARCHAR(300) NOT NULL,
    source_platform     VARCHAR(50),
    posting_count       INTEGER DEFAULT 1,
    first_seen_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_company_id BIGINT REFERENCES company(id),
    status              unmatched_status NOT NULL DEFAULT 'PENDING'
);

CREATE INDEX idx_unmatched_status ON unmatched_company (status);
CREATE UNIQUE INDEX idx_unmatched_name_source ON unmatched_company (raw_name, source_platform);

-- 크롤링 로그
CREATE TABLE crawl_log (
    id              BIGSERIAL PRIMARY KEY,
    source_type     VARCHAR(50) NOT NULL,
    source_name     VARCHAR(100) NOT NULL,
    status          crawl_status NOT NULL,
    items_collected INTEGER DEFAULT 0,
    items_new       INTEGER DEFAULT 0,
    items_duplicate INTEGER DEFAULT 0,
    error_message   TEXT,
    duration_ms     BIGINT,
    started_at      TIMESTAMP NOT NULL,
    finished_at     TIMESTAMP
);

CREATE INDEX idx_crawl_source ON crawl_log (source_type, source_name);
CREATE INDEX idx_crawl_started ON crawl_log (started_at);

-- 분석 스냅샷
CREATE TABLE analysis_snapshot (
    id              BIGSERIAL PRIMARY KEY,
    snapshot_date   DATE NOT NULL,
    analysis_type   VARCHAR(100) NOT NULL,
    data            JSONB NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshot_date ON analysis_snapshot (snapshot_date);
CREATE INDEX idx_snapshot_type ON analysis_snapshot (analysis_type);
