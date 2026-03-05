-- Part 1: 블로그 LLM 키워드 저장 컬럼
ALTER TABLE tech_blog_post ADD COLUMN IF NOT EXISTS llm_keywords JSONB DEFAULT '[]'::jsonb;

-- Part 2: 트렌드 Top N 스냅샷 테이블
CREATE TABLE IF NOT EXISTS trend_snapshot (
    id            BIGSERIAL PRIMARY KEY,
    source        trend_source NOT NULL,
    skill_name    VARCHAR(100) NOT NULL,
    rank          INTEGER NOT NULL,
    mention_count INTEGER DEFAULT 0,
    snapshot_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ts_source_time ON trend_snapshot (source, snapshot_at);
CREATE INDEX IF NOT EXISTS idx_ts_skill ON trend_snapshot (skill_name);
