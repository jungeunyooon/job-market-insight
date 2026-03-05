# DevPulse 개발 진행 기록

## Phase 0: 검증 (3일)

### Day 1 — 프로젝트 초기화
- [x] GitHub 레포 생성 및 클론
- [x] CLAUDE.md 작성
- [x] 프로젝트 구조 설계 및 태스크 분해
- [x] Docker Compose (PostgreSQL) 세팅
- [x] Spring Boot 프로젝트 초기화 (api/) — Gradle 8.12, Spring Boot 3.4.3, Java 21
- [x] Python 배치 프로젝트 초기화 (batch/) — BaseCrawler, TrendCrawler, SkillMatcher, Normalizer
- [x] Flyway 초기 마이그레이션 (전체 스키마) — 11 tables, 8 enums
- [x] 시드 데이터 파일 생성 (skills 100개, companies 29개, positions 3종)
- [x] 테스트 43개 통과 (skill_matcher 18 + normalizer 25)

### Day 2 — Phase 0 검증
- [x] 샘플 공고 20건 CSV 생성 + Phase 0 검증 파이프라인 구현
- [x] Phase 0 리포트 생성 완료 (43개 스킬 추출, Top 15 랭킹)
- [ ] 원티드 실제 API로 Backend Engineer 공고 50건+ 수집
- [ ] pandas 빈도 분석 → Top 10 기술 산출
- [ ] 결과 유용성 검증

### Day 3 — Phase 0 마무리
- [ ] Phase 0 결과 문서화
- [ ] Phase 1 진입 판단

---

## Phase 1: MVP (2주)

### Week 1 — 인프라 + 크롤러 + NLP
- [x] DB 스키마 Flyway 마이그레이션 완성 (V1__init_schema.sql)
- [x] 원티드 API 크롤러 구현 + 테스트 (10/10 통과)
- [x] BaseCrawler 인터페이스 정의
- [x] 사전 기반 skill_matcher 구현 + 테스트 (43/43 통과)
- [x] 회사명/직무명 normalizer 구현 + 테스트

### Week 2 — Spring Boot API + Streamlit
- [x] Entity/Repository 구현 (company, posting, skill) — 5 entities, 4 repositories
- [x] DTO Records 생성 (7개) — PostingResponse, SkillRankingResponse, GapAnalysisRequest 등
- [x] PostingService + PostingController + 필터링 API (10 tests)
- [x] AnalysisController (skill-ranking, company-profile, position-comparison, gap) (13 tests)
- [x] GlobalExceptionHandler (ProblemDetail RFC 7807)
- [x] Streamlit 기본 대시보드 (5페이지: 스킬 랭킹, 회사 프로필, 포지션 비교, 갭 분석, 공고 검색)

---

## Phase 2: 확장 (2주) ✅

### Week 3 — 크롤러 확장 + Trend 분석
- [x] GeekNews RSS 크롤러 (geeknews.py + 8 tests)
- [x] Jumpit 크롤러 (jumpit.py + 9 tests)
- [x] TrendPost + TrendSkill JPA Entity + Repository
- [x] BuzzHiringGapService (2×2 분류: OVERHYPED/ADOPTED/ESTABLISHED/EMERGING)
- [x] TrendController (trend-ranking, buzz-vs-hiring)
- [x] Greenhouse 크롤러 (greenhouse.py, 쿠팡/두나무 + 12 tests)
- [x] 테크 블로그 RSS 크롤러 (tech_blog.py + 8 tests)
- [x] TopicExtractor (topic_extractor.py + 9 tests)
- [x] TechBlogPost + BlogSkill JPA Entity + Repository

### Week 4 — 분석 고도화
- [x] BlogTopicTrendService (회사별 토픽, 연도별 트렌드, 스킬별 회사 분포)
- [x] BlogTopicController (3 endpoints + 4 tests)
- [x] BlogTopicTrendServiceTest (7 tests)
- [x] 리포트 자동 생성 (report/generator.py + 12 tests)
- [x] **테스트 44개 통과 (Java) + 121개 통과 (Python) = 165개**

---

## Phase 3: 서비스 고도화 (2주) ✅ (배포 제외)

### Week 5 — 백엔드 리팩토링 + 크롤러 확장
- [x] 백엔드 Package-by-Feature 리팩토링 (7 feature packages, 52 files 이동)
- [x] HackerNews Firebase API 크롤러 (hackernews.py + 20 tests)
- [x] dev.to Forem API 크롤러 (devto.py + 21 tests)

### Week 5 — React 대시보드
- [x] BuzzVsHiring 페이지 (ScatterChart + 4사분면 + KPI + 테이블)
- [x] BlogTrend 페이지 (LineChart + 회사 선택 + KPI + 테이블)
- [x] Sidebar + Router 업데이트 (7개 페이지)
- [x] `npm run build` 성공
- [x] **테스트 44개 통과 (Java) + 162개 통과 (Python) = 206개**

### 미완료 (의도적 스킵)
- [x] Docker Compose 배포 워크플로우 (`.github/workflows/deploy.yml`)
- [x] CI/CD 기초 구성 (배포 + 데이터 파이프라인 스케줄)

---

## 운영 안정화 (2026-03-05) ✅

- [x] 배포 헬스체크 방식 개선 (`curl localhost` → 컨테이너 health status 대기)
- [x] PostgreSQL enum/null 파라미터 관련 API 500 장애 수정
- [x] 배치 DB 업서트 파이프라인 구현 (`batch/pipeline/sync.py`)
- [x] 배치 실행 명령 추가 (`sync-jobs`, `sync-blogs`, `sync-trends`, `sync-all`)
- [x] 배치 컨테이너/프로파일 구성 (`batch/Dockerfile`, `docker-compose.yml`)
- [x] 정기 수집 워크플로우 추가 (`.github/workflows/data-pipeline.yml`, 6시간 주기)
- [x] 프론트 API 쿼리스트링 조립 버그 수정 (`position-comparison` 400 해결)
- [x] 회사 프로필 조회를 이름 기반으로 보강 (`company-profile` 404 완화)
- [x] 갭 분석 빈 결과(`gaps=[]`) 안내 UI 추가

---

## 데이터 파이프라인 확장 + 딥 테크니컬 키워드 (2026-03-05)

### 데이터 무결성 검증
- [x] 프로덕션 API 전수 조회: job_posting 680건, skill-ranking 421건(스킬 매핑), trend 11건
- [x] 문제 식별: 38% 공고 스킬 미매핑, 트렌드 데이터 부족, crawl_log 미사용, requiredRatio 항상 0.0

### 딥 테크니컬 키워드 모델 (ADR-008)
- [x] `skills_seed.json`에 `keywords` 필드 추가 (105개 전체)
- [x] 주요 기술 8-15개 키워드: Java(JVM 튜닝, GC 최적화), Redis(캐싱 전략, 히트율), Kafka(파티셔닝, 컨슈머 그룹) 등
- [x] Flyway V2 마이그레이션: `skill` 테이블에 `keywords JSONB DEFAULT '[]'` 컬럼 추가
- [x] `seed_reference_data()`가 keywords 필드도 함께 upsert

### 데이터 파이프라인 확장성 (ADR-007)
- [x] `crawl_log` 테이블 기록 구현: 모든 sync 실행마다 source_type/status/duration_ms/items 기록
- [x] 크롤러별 재시도 로직: 최대 2회 지수 백오프 (2초, 4초)
- [x] 컨테이너 내장 스케줄러 (`batch/scheduler.py`): `schedule` 라이브러리, 6시간 주기, `--run-now` 지원
- [x] `docker-compose.yml`에 `scheduler` 서비스 추가 (restart: unless-stopped)
- [x] GitHub Actions cron 제거 → `workflow_dispatch` 전용(수동 긴급 실행용)
- [x] **테스트 162개 통과 (Python) — 0 regression**

### 프로덕션 논리 오류 수정
- [x] `cmd_sync_all` 단일 DevPulseSync 인스턴스로 통합 (기존 3개 → 1개, seed 3회 → 1회)
- [x] `_crawl_and_sync_with_retry` 크롤링+동기화 묶어서 재시도 (기존: sync만 재시도)
- [x] `_infer_position_type` 타이틀 우선 분류 (description "react" 오분류 수정)
- [x] `is_required/is_preferred` 자격요건/우대사항 섹션 분석 기반 분류 (기존: 항상 false)
- [x] **테스트 172개 통과 (Python) — 0 regression**

---

## 딥 키워드 매칭 + LLM 요약 + API 확장 (2026-03-05)

### 딥 키워드 매칭 (ADR-009)
- [x] `_extract_matched_keywords()`: 공고 description에서 스킬별 세부 키워드 추출
- [x] `posting_skill.matched_keywords` JSONB 컬럼 추가 (V3 마이그레이션)
- [x] `sync_job_postings`에서 matched_keywords 자동 저장
- [x] Skill JPA 엔티티에 `keywords` 필드 추가
- [x] PostingSkill JPA 엔티티에 `matchedKeywords` 필드 추가
- [x] `GET /api/v1/skills/{id}/keywords` 엔드포인트 (키워드 빈도 분석)

### 스킬 마인드맵 API
- [x] `GET /api/v1/analysis/skill-mindmap?skill={name}` 엔드포인트
- [x] SkillMindmapResponse DTO (키워드 그룹, 빈도, 비율)
- [x] AnalysisControllerTest 테스트 추가

### 블로그 콘텐츠 요약
- [x] `batch/nlp/summarizer.py` extractive 요약기 (키워드 밀도 기반)
- [x] `batch/nlp/llm_summarizer.py` Ollama LLM 요약기 (ADR-011)
- [x] `sync_blog_posts`에서 LLM 우선 → extractive fallback
- [x] docker-compose에 ollama 서비스 추가 (gemma3:4b, 4GB)
- [x] `tech_blog_post.summary` 컬럼 추가 (V3 마이그레이션)

### Java 테스트 수정
- [x] AnalysisServiceTest, PostingServiceTest, BuzzHiringGapServiceTest 메서드 시그니처 수정
- [x] `./gradlew compileTestJava` 성공 (34 errors → 0)

### 테스트 현황
- [x] **테스트 191개 통과 (Python) — 0 regression**
- [x] **Java 프로덕션 + 테스트 컴파일 성공**

---

## 블로그 URL + LLM 키워드 추출 + 요구사항 정규화 (2026-03-05)

### US-014: 블로그 포스트 목록 API + URL 노출
- [x] `BlogPostListResponse` DTO 생성 (id, title, url, summary, companyName, publishedAt)
- [x] `GET /api/v1/analysis/blog-topics/posts` 페이지네이션 엔드포인트 추가
- [x] `TechBlogPostRepository`에 페이지네이션 쿼리 추가
- [x] 프론트엔드 `BlogTrend.tsx`에 최근 포스트 섹션 추가 (클릭 가능한 외부 링크)
- [x] `BlogPostListResponse` TypeScript 인터페이스 + `getBlogPosts` API 함수 추가

### US-015: LLM 키워드 추출 (ADR-012)
- [x] `batch/nlp/llm_keyword_extractor.py` — Ollama API로 심층 기술 키워드 추출
- [x] 자격요건/우대사항에서 '대규모 트래픽 처리', '캐싱 전략 설계' 등 컨텍스트 키워드 추출
- [x] V5 마이그레이션: `job_posting.llm_keywords` JSONB 컬럼 추가
- [x] `sync.py`에서 공고 동기화 시 LLM 키워드 자동 추출/저장
- [x] 10개 테스트 통과 (Ollama mock)

### US-016: LLM 요구사항 정규화 (ADR-013)
- [x] `batch/nlp/llm_normalizer.py` — Ollama API로 자격요건 정규화
- [x] 다른 표현 동일 요구사항 통일 (예: 'Java 3년 이상' → 'Java 실무 경험')
- [x] V5 마이그레이션: `job_posting.normalized_requirements` JSONB 컬럼 추가
- [x] `GET /api/v1/analysis/normalized-requirements` 집계 엔드포인트 추가
- [x] `sync.py`에서 공고 동기화 시 자동 정규화/저장
- [x] 10개 테스트 통과 (Ollama mock)

### US-017: 테스트 및 문서화
- [x] Python 272개 테스트 통과 (0 실패)
- [x] Java 컴파일 + 테스트 수정 (PostingControllerTest, AnalysisControllerTest, BlogTopicControllerTest, AnalysisServiceTest)
- [x] PROGRESS.md, DECISIONS.md 업데이트

### 동적 키워드 학습 (ADR-014)
- [x] `_update_skill_keywords_from_llm()` — LLM 추출 키워드를 스킬별로 자동 병합
- [x] 공고 동기화 시 매칭된 스킬에 새 키워드 자동 추가 (대소문자 무관 중복 제거)
- [x] 3글자 미만 키워드 필터링, 다중 스킬 분배
- [x] `test_dynamic_keywords.py` 8개 테스트 통과
- [x] **Python 280개 테스트 통과 (0 실패)**
- [x] **Java 컴파일 성공**

### 블로그 원문 크롤링 (US-018, US-019)
- [x] `tech_blog.py`에 `fetch_full_content` 옵션 구현 (RSS → 원문 HTML 크롤링)
- [x] `_fetch_page_content()`: article/main 셀렉터, PII 마스킹, 100자 미만 필터
- [x] `_enrich_with_full_content()`: RSS 요약보다 긴 원문으로 교체, 실패 시 fallback
- [x] `test_tech_blog_crawler.py`에 8개 테스트 추가 (총 16개)
- [x] `main.py`: `BLOG_FETCH_FULL_CONTENT` 환경변수로 활성화
- [x] `docker-compose.yml`: batch/scheduler에 `BLOG_FETCH_FULL_CONTENT=true` 설정
- [x] **Python 288개 테스트 통과 (0 실패)**

- [ ] 기술 블로그 시리즈

---

## 블로그 LLM 키워드 + 트렌드 스냅샷 + 3축 분석 (2026-03-05)

### Part 1: 블로그 LLM 키워드 추출 (ADR-015)
- [x] `batch/nlp/llm_blog_keyword_extractor.py` — Ollama API로 블로그 콘텐츠에서 기술 키워드 추출
- [x] 프롬프트: architecture, implementation, devops, testing 등 맥락 분류
- [x] `sync_blog_posts()`에서 LLM 키워드 자동 추출/저장 + 동적 학습 피드백
- [x] V6 마이그레이션: `tech_blog_post.llm_keywords` JSONB 컬럼 추가
- [x] `TechBlogPost` JPA 엔티티에 `llmKeywords` 필드 추가
- [x] 13개 테스트 통과 (Ollama mock)

### Part 2: 트렌드 Top N 스냅샷 (ADR-016)
- [x] V6 마이그레이션: `trend_snapshot` 테이블 (source, skill_name, rank, mention_count, snapshot_at)
- [x] `_save_trend_snapshot()` — sync 완료 후 스킬별 언급 수 집계 → 스냅샷 INSERT
- [x] `TrendSnapshot` JPA 엔티티 + `TrendSnapshotRepository`
- [x] `GET /api/v1/analysis/snapshot-history?source=GEEKNEWS&skill=React&days=30`
- [x] 8개 테스트 통과 (스냅샷 저장 로직)

### Part 3: 3축 분석 — Buzz + Hiring + Blog (ADR-017)
- [x] `ThreeAxisResponse` DTO (7가지 분류: ADOPTED, OVERHYPED, ESTABLISHED, EMERGING, PRACTICAL, HYPE_ONLY, BLOG_DRIVEN)
- [x] `BlogSkillRepository.findSkillRankingSince()` — 시간 기반 블로그 스킬 랭킹
- [x] `BuzzHiringGapService.analyzeThreeAxis()` — 3축 분류 로직
- [x] `GET /api/v1/analysis/three-axis?topN=20&days=30` 엔드포인트
- [x] 기존 `/buzz-vs-hiring` 하위호환 유지
- [x] `BuzzHiringGapServiceTest` 확장 — 3축 분류 매트릭스 + 경계값 + 통합 테스트

### Swagger 문서화 + API.md
- [x] 전체 16개 엔드포인트에 `@Operation` + `@Parameter` Swagger 어노테이션 추가
- [x] `OpenApiConfig` 설명/서버 URL 보강
- [x] `docs/API.md` 독립 마크다운 문서 생성 (16 endpoints, 파라미터, 응답 예시, enum 정의)

### 프론트엔드: 3축 분석 + 트렌드 히스토리 페이지
- [x] `ThreeAxisAnalysis.tsx` — 버블 산점도 (X=트렌드 Buzz, Y=채용 수요, 버블=블로그), 7분류 필터, 상세 테이블
- [x] `TrendHistory.tsx` — 스킬별 순위 변화 라인 차트, 소스/기간 선택, 스냅샷 현황 테이블
- [x] `types.ts` — ThreeAxisClassification, ThreeAxisItem, ThreeAxisResponse, SnapshotPoint, SnapshotHistoryResponse 추가
- [x] `endpoints.ts` — getThreeAxisAnalysis, getSnapshotHistory API 함수 추가
- [x] `Sidebar.tsx` — 3축 분석, 트렌드 히스토리 네비게이션 추가 (총 10개 페이지)
- [x] `App.tsx` — `/three-axis`, `/trend-history` 라우트 추가
- [x] `npm run build` 성공

### 테스트 현황
- [x] Python 13개 신규 테스트 통과 (블로그 LLM + 트렌드 스냅샷)
- [x] Java 컴파일 + 테스트 성공 (BuzzHiringGapServiceTest 확장)
- [x] 프론트엔드 빌드 성공 (TypeScript 0 errors)
