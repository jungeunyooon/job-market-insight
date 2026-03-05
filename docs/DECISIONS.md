# 기술적 의사결정 기록 (ADR)

## ADR-001: Polyglot Architecture (Spring Boot + Python)
- **결정**: API 서빙은 Spring Boot, 크롤링/NLP는 Python
- **이유**: 크롤링(requests, BeautifulSoup, Playwright)과 NLP(Kiwi)는 Python 생태계 압도적. API는 주력 스택인 Spring Boot로 백엔드 설계 역량 증명.
- **통신**: Phase 1은 ProcessBuilder로 Python 실행 + 공유 DB. Phase 2에서 HTTP 통신 전환.

## ADR-002: PostgreSQL 선택
- **결정**: SQLite가 아닌 PostgreSQL
- **이유**: JSONB(aliases 저장), Spring Data JPA 표준 통합, Flyway 호환, 업계 표준 RDBMS 경험. Docker Compose 한 줄로 오버헤드 최소.

## ADR-003: Dictionary Matching First
- **결정**: Phase 1은 사전 매칭만. Kiwi(Phase 2), TF-IDF(Phase 3)는 나중에.
- **이유**: 채용 공고 기술 키워드는 영어 고유명사 → 사전에 있으면 ~100% 정확. NLP는 사전 커버리지 부족이 증명된 후에 도입.

## ADR-004: TDD 원칙
- **결정**: 모든 기능은 테스트 코드가 성공 기준
- **이유**: 사용자(윤정은) 명시적 요구사항. Red→Green→Refactor 순서 엄수.

## ADR-005: 공고 영구 보관
- **결정**: 채용 공고는 절대 삭제하지 않음. ACTIVE→CLOSED→ARCHIVED 생명주기.
- **이유**: 시계열 분석 필수. 마감된 공고는 원본 사라짐. 10,000건 = ~100MB로 저장 공간 문제 없음.

## ADR-006: 배치 업서트 + 주기 실행
- **결정**: 배치는 크롤링 결과를 즉시 DB에 upsert하고, 컨테이너 내장 스케줄러로 6시간마다 자동 실행.
- **이유**: 수집 결과가 메모리/로그에만 남으면 서비스 데이터가 비어 있는 상태가 지속됨. 운영에서는 정기 동기화가 필수.
- **변경 이력**: 초기에는 GitHub Actions SSH 기반 cron → 컨테이너 내장 스케줄러로 전환 (ADR-007 참조)

## ADR-007: 데이터 파이프라인 자체 스케줄링 전환
- **결정**: GitHub Actions SSH 기반 cron 대신, 배치 컨테이너 내부에 스케줄러(`scheduler.py`)를 내장하여 자체적으로 6시간 주기 실행.
- **이유**:
  - GitHub Actions SSH는 외부 의존성(GitHub 가용성, SSH 키 관리, 네트워크)이 많아 프로덕션 서비스 신뢰성 부족
  - 컨테이너 내장 스케줄러는 `docker compose up` 한 번으로 전체 서비스(API + 프론트 + 배치)가 동작
  - 크롤링 실행마다 `crawl_log` 테이블에 기록하여 관측성(observability) 확보
  - 크롤러별 장애 격리 + 최대 2회 재시도로 안정성 향상
- **GitHub Actions**: `workflow_dispatch` 전용(수동 긴급 실행용)으로 유지, cron 스케줄 제거
- **관측성**: 모든 크롤링 실행은 `crawl_log` 테이블에 source_type, source_name, status, items_collected, items_new, duration_ms, error_message 기록

## ADR-008: 딥 테크니컬 키워드 모델
- **결정**: skills_seed.json의 각 기술에 `keywords` 필드 추가. 단순 기술명(Redis, Kafka) 대신 해당 기술의 핵심 개념 키워드(캐싱 전략, 캐시 미스, 히트율, 파티셔닝, 컨슈머 그룹 등)를 관리.
- **이유**:
  - 현재: "Redis를 사용한다" 수준의 단순 매칭만 가능
  - 목표: "Redis의 어떤 측면(캐싱, pub/sub, 클러스터링)을 사용하는가" 수준의 심층 분석
  - 테크 블로그 분석 시 기술의 구체적 활용 맥락을 파악 가능
  - 향후: 기술 서적 기반 키워드 확장, 테크 블로그 자동 키워드 추출
- **스키마**: `skill` 테이블에 `keywords JSONB DEFAULT '[]'` 컬럼 추가 (V2 마이그레이션)
- **데이터 소스**: 한국 테크 기업 엔지니어링 블로그, 기술 면접 빈출 개념, 시스템 설계 토론 주제
- **확장 계획**: Phase 2에서 책 첨부 → 키워드 자동 추출, 테크 블로그 크롤링 → 키워드 자동 학습

## ADR-009: 딥 키워드 매칭 — 공고에서 세부 기술 키워드 추출 (2026-03-05)

### 상태: 승인

### 맥락
- 기존 스킬 매칭은 "Redis", "Kafka" 같은 기술명만 추출
- 실제 채용 시장에서 중요한 것은 "캐싱 전략", "TTL 설계", "파티셔닝" 같은 세부 키워드
- skills_seed.json에 이미 keywords 필드가 추가되어 있음 (ADR-008)

### 결정
- 스킬 매칭 시 해당 스킬의 keywords를 description에서 추가 검색
- `posting_skill.matched_keywords` JSONB 컬럼에 매칭된 세부 키워드 저장 (V3 마이그레이션)
- `GET /api/v1/skills/{id}/keywords` API로 키워드별 공고 빈도 조회
- `GET /api/v1/analysis/skill-mindmap?skill={name}` API로 마인드맵용 계층 데이터 제공

### 결과
- 채용 시장의 기술 깊이를 정량적으로 분석 가능
- 스킬별 실무 키워드 트렌드 파악 (예: Redis에서 "캐싱 전략" 60%, "클러스터" 30%)
- 마인드맵 시각화로 기술 학습 방향 제시 가능

## ADR-010: 블로그 콘텐츠 요약 — extractive + LLM 이중 전략 (2026-03-05)

### 상태: 승인

### 맥락
- 테크 블로그 원문은 길어서 트렌드 분석에 활용하기 어려움
- 블로그의 핵심 기술 인사이트를 요약하면 스킬-컨텍스트 연결이 풍부해짐
- 외부 API 비용 없이 로컬에서 처리해야 함

### 결정
- 1단계: extractive 요약 (`nlp/summarizer.py`) — 키워드 밀도 기반 문장 3개 선택
- 2단계: Ollama LLM 요약 (`nlp/llm_summarizer.py`) — 로컬 모델로 구조화 요약
- `OLLAMA_HOST` 환경변수 있으면 LLM 우선, 없으면 extractive fallback
- `tech_blog_post.summary` TEXT 컬럼에 저장 (V3 마이그레이션)

### 결과
- 블로그 요약이 스킬 트렌드 분석의 컨텍스트로 활용 가능
- LLM 없이도 기본 요약 제공 (extractive)
- LLM 모델 교체가 환경변수로 간편 (OLLAMA_MODEL)

## ADR-011: Ollama 기반 로컬 LLM 블로그 요약 (2026-03-05)

### 상태: 승인

### 맥락
- 블로그 요약의 품질을 높이기 위해 LLM 기반 요약이 필요
- 외부 API(Claude, GPT) 비용과 의존성을 피하기 위해 로컬 LLM 선택
- 홈서버에 Docker로 Ollama를 배포하여 비용 제로로 운영

### 결정
- Ollama를 docker-compose 서비스로 추가 (ollama/ollama 이미지)
- gemma3:4b 모델을 기본값으로 사용 (한국어 지원, 4GB 메모리 내 동작)
- OLLAMA_HOST 환경변수로 활성화, 미설정 시 extractive 요약으로 자동 fallback
- 배치 파이프라인에서 블로그 동기화 시 LLM 요약 생성

### 결과
- 기술 블로그 요약 품질 대폭 향상 (한국어 3-5문장 구조화 요약)
- Ollama 장애 시에도 서비스 중단 없음 (extractive fallback)
- 모델 교체가 환경변수 하나로 가능 (OLLAMA_MODEL)

## ADR-012: LLM 기반 심층 키워드 추출 (2026-03-05)

### 상태: 승인

### 맥락
- 기존 사전 매칭은 "Redis", "Kafka" 같은 기술명만 추출
- 실제 채용 시장에서 중요한 것은 "대규모 트래픽 처리 경험", "캐싱 전략 설계", "MSA 아키텍처 전환" 같은 컨텍스트 키워드
- skills_seed.json의 키워드는 수동 관리 → LLM으로 자동 추출 가능

### 결정
- `batch/nlp/llm_keyword_extractor.py` — Ollama API로 자격요건/우대사항에서 심층 키워드 자동 추출
- `job_posting.llm_keywords` JSONB 컬럼에 `[{keyword, section}]` 형태로 저장 (V5 마이그레이션)
- `sync_job_postings()`에서 공고 동기화 시 자동 호출
- `OLLAMA_HOST` 미설정 시 빈 리스트 반환 (graceful fallback)

### 결과
- 채용 공고의 실무 역량 요구사항을 정량적으로 분석 가능
- 스킬 마인드맵과 결합하여 기술별 실무 요구 트렌드 파악
- LLM 응답 파싱 실패 시에도 파이프라인 중단 없음

## ADR-013: LLM 기반 자격요건 정규화 (2026-03-05)

### 상태: 승인

### 맥락
- 같은 요구사항이 공고마다 다르게 표현됨: "Java 경험 3년 이상", "Java 기반 백엔드 개발 경험", "자바 서버 개발자"
- 단순 텍스트 비교로는 동일 요구사항을 하나로 묶을 수 없음
- 이를 정규화하면 채용 시장의 실제 요구사항 트렌드를 정확하게 분석 가능

### 결정
- `batch/nlp/llm_normalizer.py` — Ollama API로 자격요건/우대사항 텍스트를 정규화
- 정규화 결과: `[{original, normalized, category}]` (category: technical/experience/soft_skill/education/domain)
- `job_posting.normalized_requirements` JSONB 컬럼에 저장 (V5 마이그레이션)
- `GET /api/v1/analysis/normalized-requirements` — 정규화된 요구사항 집계 API (네이티브 JSONB 쿼리)
- `OLLAMA_HOST` 미설정 시 빈 리스트 반환 (graceful fallback)

### 결과
- "Java 3년" + "Java 기반 개발" + "자바 서버" → "Java 실무 경험"으로 통일
- 채용 시장에서 가장 많이 요구하는 역량을 정확한 순위로 제공
- 경력 연수 등 불필요한 정보 제거, 핵심 역량만 추출

## ADR-014: 동적 키워드 학습 — LLM 추출 키워드 자동 피드백 (2026-03-05)

### 상태: 승인

### 맥락
- 기존: `skills_seed.json`에 키워드를 수동으로 사전 정의
- 한계: 채용 시장에서 실제로 요구하는 키워드를 미리 다 파악할 수 없음
- LLM 키워드 추출(ADR-012)이 이미 공고별 실무 키워드를 추출하고 있음

### 결정
- `sync_job_postings()`에서 LLM 추출 키워드를 매칭된 스킬의 `keywords` 필드에 자동 병합
- `_update_skill_keywords_from_llm()` 메서드: 대소문자 무관 중복 제거, 3글자 미만 필터링
- DB `skill.keywords` JSONB와 인메모리 `skill_keywords` 캐시 동시 업데이트
- 공고가 쌓일수록 키워드가 자동으로 풍부해지는 피드백 루프

### 결과
- 수동 키워드 관리 부담 제거
- 실제 채용 시장 데이터 기반 키워드 → 매칭 정확도 향상
- 시간이 지날수록 스킬별 키워드가 자동으로 정교해짐

## ADR-015: 블로그 LLM 키워드 추출 (2026-03-05)

### 상태: 승인

### 맥락
- 기존 블로그 분석은 사전 매칭만 사용 — 채용 공고보다 키워드 정확도 낮음
- 채용 공고에는 LLM 키워드 추출(ADR-012) + 동적 학습(ADR-014)이 적용되어 있음
- 블로그에도 동일한 파이프라인을 적용하면 채용 vs 실무 키워드 비교 가능

### 결정
- `batch/nlp/llm_blog_keyword_extractor.py` — 블로그 콘텐츠에서 기술 키워드 + 맥락(context) 추출
- context 분류: architecture, implementation, devops, testing, data, infra
- `tech_blog_post.llm_keywords` JSONB 컬럼에 `[{keyword, context}]` 저장 (V6 마이그레이션)
- `sync_blog_posts()`에서 추출 후 `_update_skill_keywords_from_llm()` 동적 학습 연계

### 결과
- 채용 공고(section: 자격요건/우대) vs 블로그(context: architecture/implementation) 키워드 비교 가능
- 블로그 기반 동적 키워드 학습으로 사전 커버리지 자동 확대
- Ollama 미설정 시 기존 사전 매칭만 동작 (graceful fallback)

## ADR-016: 트렌드 Top N 스냅샷 (2026-03-05)

### 상태: 승인

### 맥락
- 기존 트렌드 분석은 "현재 시점" 집계만 가능 — 시계열 비교 불가
- "React가 2주 전에는 1위였는데 지금은 3위" 같은 순위 변화 추적 필요

### 결정
- `trend_snapshot` 테이블: source(GEEKNEWS/HN/DEVTO), skill_name, rank, mention_count, snapshot_at
- `sync_trend_posts()` 완료 시 `_save_trend_snapshot()` 자동 호출 (최근 30일 기준 Top 20 집계)
- `GET /api/v1/analysis/snapshot-history?source=GEEKNEWS&skill=React&days=30` API

### 결과
- 시점별 트렌드 순위 변화 시각화 가능 (라인 차트)
- 동기화할 때마다 자동 스냅샷 → 추가 스케줄링 불필요
- source별 독립 스냅샷 → 플랫폼 간 트렌드 비교 가능

## ADR-017: 3축 분석 — Buzz + Hiring + Blog (2026-03-05)

### 상태: 승인

### 맥락
- 기존 Buzz vs Hiring은 2축(커뮤니티 관심 vs 채용 수요) → 4가지 분류만 가능
- 블로그(현업 실무)를 3번째 축으로 추가하면 새로운 인사이트 도출 가능
- 예: Java는 커뮤니티에서 "뜨거운 화제"는 아니지만, 채용+블로그에서는 압도적 → PRACTICAL

### 결정
- 7가지 3축 분류:
  - ADOPTED: trend HIGH + job HIGH (blog 무관) — 시장 + 커뮤니티 모두 채택
  - HYPE_ONLY: trend HIGH + job LOW + blog LOW — 과대광고
  - OVERHYPED: trend HIGH + job LOW + blog HIGH — 커뮤니티 관심 + 실무 글 있지만 채용 수요 낮음
  - PRACTICAL: trend LOW + job HIGH + blog HIGH — 조용히 쓰이는 기술
  - ESTABLISHED: trend LOW + job HIGH + blog LOW — 정착된 기술
  - BLOG_DRIVEN: trend LOW + job LOW + blog HIGH — 블로그에서만 화제
  - EMERGING: trend LOW + job LOW + blog LOW — 태동기
- Thresholds: HIGH_TREND=5%, HIGH_JOB=10%, HIGH_BLOG=5%
- `GET /api/v1/analysis/three-axis?topN=20&days=30` 새 엔드포인트
- 기존 `/buzz-vs-hiring` 하위호환 유지

### 결과
- PRACTICAL 분류로 "조용히 쓰이는 실무 기술" 식별 가능
- HYPE_ONLY vs OVERHYPED 구분으로 블로그에서 실무 논의되는지 판별
- BLOG_DRIVEN으로 채용 시장에 아직 반영 안 된 실무 트렌드 선점 가능
