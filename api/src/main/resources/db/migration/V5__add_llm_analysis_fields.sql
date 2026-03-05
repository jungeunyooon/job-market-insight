-- V5: Add LLM analysis fields to job_posting
-- llm_keywords: contextual keywords extracted by LLM (e.g., "대규모 트래픽 처리", "캐싱 전략 설계")
-- normalized_requirements: requirements normalized by LLM for cross-posting comparison

ALTER TABLE job_posting ADD COLUMN IF NOT EXISTS llm_keywords JSONB DEFAULT '[]'::jsonb;
ALTER TABLE job_posting ADD COLUMN IF NOT EXISTS normalized_requirements JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN job_posting.llm_keywords IS 'LLM으로 추출한 심층 기술 키워드 [{keyword, section}]';
COMMENT ON COLUMN job_posting.normalized_requirements IS 'LLM으로 정규화한 자격요건 [{original, normalized, category}]';
