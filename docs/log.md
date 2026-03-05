# DevPulse 개발 로그

> 채용시장 기술 트렌드 분석 서비스 — 구현 기록
> Repo: `job-market-insight/`

---

## 2026-03-04 | Phase 0 + Phase 1 Week 1 — 프로젝트 스캐폴딩

### 진행 내용

**프로젝트 초기화 완료** — GitHub repo `job-market-insight` 클론 후 전체 스캐폴딩:

1. **CLAUDE.md 작성**: TDD 원칙, Git 워크플로, 코드 컨벤션, 아키텍처 결정사항 문서화
2. **Docker Compose**: PostgreSQL 16 Alpine + 헬스체크 설정
3. **Spring Boot 프로젝트 (api/)**:
   - build.gradle: Spring Boot 3.4.3, Java 21, Spring Data JPA, QueryDSL 5.1, Flyway, Testcontainers
   - Gradle wrapper 8.12 생성
   - application.yml + application-test.yml (Testcontainers JDBC URL)
   - DevPulseApplication.java + contextLoads 테스트
4. **Flyway 마이그레이션 V1__init_schema.sql**:
   - 11개 테이블: company, job_posting, skill, posting_skill, tech_blog_post, blog_skill, trend_post, trend_skill, unmatched_company, crawl_log, analysis_snapshot
   - 8개 ENUM 타입, 인덱스, unique constraints 전부 포함
   - PRD v3.0 Section 5.1 ERD 완전 반영
5. **Python 배치 프로젝트 (batch/)**:
   - BaseCrawler ABC + RawJobPosting 데이터클래스
   - TrendCrawler ABC + TrendPost 데이터클래스
   - SkillMatcher: 사전 기반 매칭, 복합 키워드 우선, scope 필터링
   - PositionNormalizer + CompanyNormalizer
6. **시드 데이터 (data/)**:
   - skills_seed.json: 100개 기술 (13 language, 21 framework, 10 database, 4 messaging, 22 devops, 12 concept, 11 ai_ml_model, 12 ai_ml_devtool)
   - companies_seed.json: 29개 회사 (Big 7 + 자회사 5 + 유니콘 8 + 스타트업 4 + SI 2 + MID 2)
   - position_aliases.json: BACKEND/PRODUCT/FDE 매핑
7. **테스트 코드 43개 전부 통과**:
   - test_skill_matcher.py: 18개 (기본 매칭, 복합 키워드, 중복 제거, 경계 처리, scope 필터링, 엣지 케이스, 시드 파일 로딩)
   - test_normalizer.py: 25개 (포지션 정규화 14개 + 회사명 정규화 11개)
8. **Phase 0 검증 파이프라인 구현**:
   - sample_postings.csv: 20건 샘플 공고 (네카라쿠배당토 + 유니콘 + 스타트업)
   - phase0_validate.py: CSV → SkillMatcher → pandas 빈도 분석 → Markdown 리포트
   - 테스트 10개 통과 (CSV 로딩, 스킬 추출, 빈도 분석, 카테고리 분석, 리포트 생성)
   - **검증 결과**: Java 100%, Spring Boot 95%, Docker 85%, MySQL 80%, Kafka 65% — 직관과 일치
9. **Spring Boot Entity 클래스 구현**:
   - Company (JSONB tags/aliases), Skill (source_scope ENUM), JobPosting (영구 보관 생명주기), PostingSkill
   - Repository 인터페이스: 필터링 쿼리 (카테고리, 포지션, 상태), 스킬 랭킹 집계 쿼리
10. **원티드 API 크롤러 (WantedAPICrawler)**:
    - 키워드 검색 → 중복 제거 → 상세 조회 → RawJobPosting 변환
    - Rate limit (1 req/sec), 429 자동 재시도, 개인정보 마스킹
    - 테스트 10개 통과 (목록 조회, 상세 조회, 에러 처리, 풀 파이프라인, 크로스 키워드 중복 제거)

### 버그 수정
- **한글 조사 경계 문제**: `(?<![a-zA-Z가-힣])` → 영어/한글 경계 패턴 분리

### 산출물
- 테스트 **63개 전부 통과** (normalizer 25 + skill_matcher 18 + phase0 10 + wanted_crawler 10)

---

## 2026-03-04 | Phase 1 Week 2 — Spring Boot REST API + Dashboard

### 진행 내용

11. **DTO Records 생성 (7개)**:
    - PostingResponse, PostingDetailResponse, SkillRankingResponse, CompanyProfileResponse, PositionComparisonResponse, GapAnalysisRequest, GapAnalysisResponse
12. **Repository 확장**:
    - JobPostingRepository: findByFiltersExtended, findByFiltersWithSkills, countByCompanyIdGroupByPositionType
    - PostingSkillRepository: findSkillRankingWithFilters, countPostingsWithFilters, findPositionBreakdownByCompany
13. **Service 계층 구현**:
    - PostingService: findAll (7개 필터 + 페이징), findById
    - AnalysisService: getSkillRanking, getCompanyProfile, getPositionComparison, analyzeGap
14. **Controller 구현**:
    - PostingController: GET /api/v1/postings, GET /api/v1/postings/{id}
    - AnalysisController: skill-ranking, company-profile/{id}, position-comparison, POST gap
    - GlobalExceptionHandler: ProblemDetail (RFC 7807)
15. **테스트 23개 작성 (전부 통과)**:
    - PostingServiceTest (6), AnalysisServiceTest (7), PostingControllerTest (4), AnalysisControllerTest (6)
16. **Streamlit 대시보드 (dashboard/)**:
    - 5개 페이지, 데모 모드, Plotly 차트, 갭 분석 시각화

### 버그 수정
- **List.of() varargs 모호성**: `List.<Object[]>of(...)` 명시적 타입 힌트
- **갭 분석 CRITICAL 조건**: 테스트 데이터 40% → 60% 수정
- **contextLoads Docker**: `@EnabledIf("isDockerAvailable")` 조건부 실행

### 산출물
- **전체 테스트 86개 통과** (Java 23 + Python 63)

---

## 2026-03-04 | Phase 2 Week 3 — 크롤러 확장 + Trend 분석

### 진행 내용

17. **GeekNews RSS 크롤러 (geeknews.py)**: feedparser, TrendCrawler ABC, 8 tests
18. **Jumpit 크롤러 (jumpit.py)**: JSON API, BaseCrawler, 9 tests
19. **TrendPost + TrendSkill JPA Entities**: source ENUM, Repository (기간별 스킬 랭킹)
20. **BuzzHiringGapService**: 2×2 분류 (OVERHYPED/ADOPTED/ESTABLISHED/EMERGING), 임계값 trend≥5% job≥10%, 6 tests
21. **TrendController**: trend-ranking, buzz-vs-hiring, 3 MockMvc tests

### 산출물
- **전체 테스트 112개 통과** (Java 32 + Python 80)

---

## 2026-03-04 | Phase 2 Week 3-4 — 테크 블로그 + BlogTopicTrend API

### 진행 내용

22. **테크 블로그 RSS 크롤러 (tech_blog.py)**:
    - feedparser 기반, 5개 회사 블로그 (네이버/카카오/배민/당근/쿠팡)
    - BLOG_CONFIGS 딕셔너리 패턴, 8 tests
23. **TopicExtractor (topic_extractor.py)**:
    - SkillMatcher 기반, title > tags > content 우선순위 dedup, 9 tests
24. **TechBlogPost + BlogSkill JPA Entities**:
    - TechBlogPostRepository: countByCompanyGroupByYear, countByCompanyId
    - BlogSkillRepository: findSkillRankingByCompanyAndYear, findYearlySkillTrend, findCompanyDistributionBySkill
25. **BlogTopicTrendService**: 회사별 토픽, 연도별 트렌드, 스킬별 회사 분포, 7 tests
26. **BlogTopicController**: 3 GET endpoints, 4 MockMvc tests
27. **3개 DTO Records**: BlogTopicResponse, YearlyTrendResponse, SkillCompanyDistributionResponse
28. **GlobalExceptionHandler**: IllegalArgumentException → 400 핸들러 추가

### 버그 수정
- **GeekNews published_parsed**: `hasattr` → `entry.get()` (dict key)
- **TopicExtractor dict 접근**: `m["name"]` → `m.skill_name` (MatchedSkill dataclass)
- **SkillMatcher 리스트 초기화**: isinstance 분기로 list[dict] 직접 전달 지원

### 산출물
- **전체 테스트 141개 통과** (Java 44 + Python 97)

---

## 2026-03-04 | Phase 2 마무리 — Greenhouse 크롤러 + 리포트 자동 생성

### 진행 내용

29. **Greenhouse Board API 크롤러 (greenhouse.py)**:
    - Greenhouse 공개 Board API 사용 (boards-api.greenhouse.io/v1)
    - 쿠팡/두나무 board token 기본 설정, 확장 가능
    - HTML 콘텐츠 → 플레인텍스트 변환 (_HTMLTextExtractor)
    - 개인정보 마스킹 (이메일/전화번호)
    - 12 tests (초기화, 목록, 빈 보드, API 에러, 상세, HTML 제거, 풀 파이프라인, 멀티 보드)

30. **리포트 자동 생성 (report/generator.py)**:
    - ReportData 데이터클래스 (스킬 랭킹, 회사 프로필, 포지션 비교, Buzz vs Hiring, 블로그 트렌드)
    - ReportGenerator: 5개 섹션 Markdown 생성 + 파일 저장
    - 빈 데이터/부분 데이터 graceful 처리
    - 12 tests (마크다운 생성, 섹션별 검증, 파일 저장, 빈/부분 데이터)

### 산출물
- **전체 테스트 165개 통과** (Java 44 + Python 121)
- **Phase 2 완료**

---

## 2026-03-04 | Phase 3 Week 5 — 백엔드 리팩토링 + 크롤러 확장 + React 대시보드

### 진행 내용

31. **백엔드 Package-by-Feature 리팩토링**:
    - layer 기반 → feature 기반 패키지 구조 전환 (Context7 MCP 참고)
    - 7개 feature 패키지: posting, analysis, trend, blog, company, skill, global
    - Controller + Service + DTO + Entity + Repository 동일 패키지에 co-locate
    - 52개 Java 소스 파일 이동 + 패키지 선언/import 경로 일괄 수정
    - JPQL fully-qualified 참조(`com.devpulse.posting.PostingStatus.ACTIVE`) 업데이트
    - `./gradlew compileJava` → BUILD SUCCESSFUL, 전체 테스트 통과

32. **HackerNews Firebase API 크롤러 (hackernews.py)**:
    - `/topstories.json` → `/item/{id}.json` 2단계 조회
    - TrendCrawler ABC 확장, story 타입만 필터, rate limit 0.5s
    - 20 tests (초기화, fetch, item 변환, 풀 파이프라인)

33. **dev.to Forem API 크롤러 (devto.py)**:
    - `https://dev.to/api/articles` tag/per_page/page 파라미터
    - ISO 8601 날짜 파싱, 빈 title/url 스킵
    - 21 tests (초기화, fetch, article 변환, 풀 파이프라인)

34. **React 대시보드 확장 (frontend/)**:
    - **BuzzVsHiring.tsx**: ScatterChart + 4사분면 (OVERHYPED/ADOPTED/ESTABLISHED/EMERGING), ReferenceLine 임계선, 분류 필터, KPI 카드, 상세 테이블
    - **BlogTrend.tsx**: LineChart 연도별 스킬 트렌드, 회사 선택, KPI 카드, 인라인 바 차트
    - Sidebar 네비게이션 2개 추가 (Buzz vs 채용, 블로그 트렌드)
    - App.tsx 라우트 추가 (/buzz, /blog-trend)
    - `npm run build` → 성공 (tsc + vite)

### 산출물
- **전체 테스트 206개 통과** (Java 44 + Python 162)
- **Phase 3 완료** (배포 제외)

---

## 2026-03-05 | 운영 배포 안정화 + 데이터 파이프라인 구현 (Codex 협업)

### Codex와의 대화 기반 작업 기록

35. **배포 헬스체크 실패 원인 분리**:
    - 프론트엔드 빌드는 성공, 실패 지점은 API readiness check
    - 기존 GitHub Actions가 `localhost:8080` 직접 curl로 확인하던 방식 수정
    - 컨테이너 헬스 상태(`docker inspect ... State.Health.Status`) 기준으로 변경
    - `docker-compose.yml`의 obsolete `version` 키 제거

36. **데이터 공백 원인 확인**:
    - 로컬 Docker DB 직접 점검 결과 핵심 테이블 데이터 0건 확인
    - `batch/main.py`가 크롤링 출력만 하고 DB 저장 경로가 없음을 확인
    - 즉, 기존 배포환경에는 정기 데이터 적재 파이프라인이 부재

37. **API 500 장애 긴급 수정**:
    - PostgreSQL ENUM 바인딩 이슈(`position_type = varchar`) 해결
    - Hibernate `@JdbcTypeCode(SqlTypes.NAMED_ENUM)` 적용
    - JPQL enum 상수/`null` 파라미터 패턴으로 발생하던 타입 추론 에러 수정
    - 수정 후 `/api/v1/postings`, `/api/v1/analysis/skill-ranking`, `/api/v1/analysis/buzz-vs-hiring` 200 확인

38. **실제 업서트 파이프라인 구현**:
    - `batch/pipeline/sync.py` 신규: 크롤링 결과를 DB upsert
    - `sync-jobs`, `sync-blogs`, `sync-trends`, `sync-all` 명령 추가
    - 시드 데이터(`skills_seed.json`, `companies_seed.json`)를 먼저 upsert 후 참조 무결성 보장
    - `posting_skill`, `blog_skill`, `trend_skill` 연결 테이블까지 반영

39. **배포환경 정기 실행 경로 추가**:
    - `batch/Dockerfile` 추가
    - `docker-compose.yml`에 `batch` 서비스(profile: `batch`) 추가
    - `.github/workflows/data-pipeline.yml` 신규:
      - `workflow_dispatch`(수동 실행)
      - `cron: 0 */6 * * *` (6시간 주기)
      - 서버에서 `docker compose --profile batch run --rm batch sync-all` 실행

40. **커밋/푸시 내역 (Codex 대화 세션에서 반영)**:
    - `7808348` fix(deploy): use container health status in API readiness check
    - `1cbe268` fix(api): resolve enum query failures on postgres
    - `96a7756` feat(batch): add crawl-to-db upsert pipeline and scheduled sync

41. **분석 API 화면 오류 후속 수정 (Codex 협업)**:
    - `position-comparison` 400 원인: 프론트 API 클라이언트 쿼리스트링 중복 조립 버그
    - `company-profile/1` 404 원인: 프론트의 회사 ID 하드코딩과 운영 DB ID 불일치
    - `gap` 빈 화면 개선: `gaps=[]`일 때 데이터 미수집 안내 UI 추가
    - 회사 프로필 이름 기반 조회 API(`/api/v1/analysis/company-profile?companyName=...`) 추가

---

## 2026-03-05 | 데이터 파이프라인 확장 + 딥 테크니컬 키워드

### 진행 내용

42. **프로덕션 데이터 무결성 검증**:
    - 프로덕션 API(`job.jungeun.cloud`) 전수 조회: 680 postings, 421 with skills, 11 trends
    - 38% 공고 스킬 미매핑 식별, 트렌드 데이터 부족(11건), crawl_log 미사용 확인
    - FDE 포지션의 Linux 42.3% 이상치 → position_type 추론 로직 개선 필요 (향후)

43. **딥 테크니컬 키워드 모델 구축**:
    - `skills_seed.json` 105개 전 항목에 `keywords` 필드 추가
    - 주요 기술 8-15개 심층 키워드: Redis(캐싱 전략, 히트율, TTL), Kafka(파티셔닝, exactly-once), Java(JVM 튜닝, GC 최적화) 등
    - 키워드 소스: 한국 테크 기업 블로그 용어, 기술 면접 빈출 개념, 시스템 설계 토론 주제
    - Flyway V2 마이그레이션: `ALTER TABLE skill ADD COLUMN keywords JSONB DEFAULT '[]'`
    - `seed_reference_data()` 수정: keywords 필드 upsert 포함

44. **데이터 파이프라인 확장성 개선**:
    - `sync.py`에 `log_crawl_execution()` 메서드 추가: crawl_log 테이블에 실행 결과 기록
    - 3개 sync 메서드(sync_job_postings/sync_blog_posts/sync_trend_posts) 타이밍 + 로깅 추가
    - `main.py`에 `_sync_with_retry()` 추가: 크롤러별 최대 2회 재시도, 지수 백오프(2s, 4s)
    - 각 sync 명령 실행 후 PASS/FAIL 요약 출력

45. **컨테이너 내장 스케줄러 전환**:
    - `batch/scheduler.py` 신규: `schedule` 라이브러리, 6시간 주기, `--interval`/`--run-now` 인자
    - `docker-compose.yml`에 `scheduler` 서비스 추가 (restart: unless-stopped, --run-now)
    - GitHub Actions `data-pipeline.yml`에서 cron 스케줄 제거 → workflow_dispatch 전용

46. **문서 업데이트**:
    - `docs/DECISIONS.md`: ADR-007 (파이프라인 자체 스케줄링), ADR-008 (딥 테크니컬 키워드)
    - `docs/PROGRESS.md`: 데이터 파이프라인 확장 섹션 추가
    - `docs/log.md`: 본 세션 작업 기록
    - `docs/PROJECT_DOCS.md`: 키워드 모델 + 파이프라인 아키텍처 반영

### 산출물
- **테스트 162개 통과 (Python) — 0 regression**
- **기존 Java 44개 테스트 영향 없음** (스키마 V2는 ADD COLUMN only)

---

## 2026-03-05 | 프로덕션 논리 오류 수정 + 딥 키워드 매칭 + LLM 요약

### 진행 내용

47. **프로덕션 논리 오류 6개 발견 및 4개 수정**:
    - `cmd_sync_all` DevPulseSync 3개 생성 → 1개로 통합 (seed 3회 → 1회)
    - `_crawl_and_sync_with_retry` 크롤링+동기화 묶어서 재시도 (네트워크 장애 시 재크롤)
    - `_infer_position_type` 타이틀 우선 분류 (description "react" 오분류 수정)
    - `_classify_skill_requirement` 자격요건/우대사항 섹션 분석 (is_required/is_preferred 실제 값)

48. **딥 키워드 매칭 구현 (ADR-009)**:
    - `_extract_matched_keywords()`: 스킬 매칭 시 세부 키워드도 description에서 추출
    - `posting_skill.matched_keywords` JSONB 컬럼 (V3 마이그레이션)
    - `_skill_keywords` 딕셔너리: skills_seed.json keywords를 런타임 조회용으로 캐시
    - `GET /api/v1/skills/{id}/keywords` API: 키워드별 공고 빈도 분석

49. **스킬 마인드맵 API 구현**:
    - `GET /api/v1/analysis/skill-mindmap?skill={name}` 엔드포인트
    - SkillMindmapResponse: 키워드 그룹, 공고 빈도, 비율 포함
    - PostingSkillRepository에 `findKeywordFrequenciesBySkillId` 네이티브 쿼리 추가

50. **블로그 콘텐츠 요약 구현**:
    - `batch/nlp/summarizer.py`: extractive 요약 (키워드 밀도 + 위치 + 숫자 보너스)
    - `batch/nlp/llm_summarizer.py`: Ollama API 호출 (ADR-011)
    - `sync_blog_posts`에서 LLM 우선 → extractive fallback 체인
    - docker-compose에 ollama 서비스 추가 (gemma3:4b, 4GB 제한)

51. **Java 테스트 컴파일 오류 수정**:
    - AnalysisServiceTest, PostingServiceTest, BuzzHiringGapServiceTest mock 시그니처 수정
    - 34 errors → 0 errors

52. **Skill/PostingSkill JPA 엔티티 업데이트**:
    - Skill: `keywords List<String>` JSONB 필드 추가
    - PostingSkill: `matchedKeywords List<String>` JSONB 필드 추가

### 산출물
- **테스트 191개 통과 (Python) — 0 regression** (162 → 191: +29 신규)
- **Java 프로덕션 + 테스트 컴파일 성공**
- **Flyway V3 마이그레이션**: matched_keywords + summary 컬럼
- **신규 API**: `/skills/{id}/keywords`, `/analysis/skill-mindmap`
- **ADR-009** (딥 키워드 매칭), **ADR-011** (Ollama LLM 요약)
