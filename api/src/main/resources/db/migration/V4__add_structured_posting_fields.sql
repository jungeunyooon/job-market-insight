-- 채용 공고 구조화 필드 추가
-- 자격요건, 우대사항, 담당업무, 기술스택, 복리후생 등을 별도 컬럼으로 보존
-- 기존 description_raw는 원문 전체를 유지 (하위 호환)

ALTER TABLE job_posting
    ADD COLUMN requirements_raw     TEXT,
    ADD COLUMN preferred_raw        TEXT,
    ADD COLUMN responsibilities_raw TEXT,
    ADD COLUMN tech_stack_raw       TEXT,
    ADD COLUMN benefits_raw         TEXT,
    ADD COLUMN company_size         VARCHAR(100),
    ADD COLUMN team_info            TEXT,
    ADD COLUMN hiring_process       TEXT,
    ADD COLUMN employment_type      VARCHAR(50),
    ADD COLUMN work_type            VARCHAR(50);

COMMENT ON COLUMN job_posting.requirements_raw IS '자격요건 원문';
COMMENT ON COLUMN job_posting.preferred_raw IS '우대사항 원문';
COMMENT ON COLUMN job_posting.responsibilities_raw IS '담당업무 원문';
COMMENT ON COLUMN job_posting.tech_stack_raw IS '기술스택 (태그/텍스트)';
COMMENT ON COLUMN job_posting.benefits_raw IS '복리후생 / 근무조건';
COMMENT ON COLUMN job_posting.company_size IS '회사 규모 (예: 50-100명)';
COMMENT ON COLUMN job_posting.team_info IS '팀 소개';
COMMENT ON COLUMN job_posting.hiring_process IS '채용 프로세스';
COMMENT ON COLUMN job_posting.employment_type IS '고용 형태 (정규직/계약직/인턴)';
COMMENT ON COLUMN job_posting.work_type IS '근무 형태 (원격/하이브리드/출근)';
