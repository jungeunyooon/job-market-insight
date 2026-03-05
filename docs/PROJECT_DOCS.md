# DevPulse 프로젝트 문서

> 개발자 채용시장 기술 트렌드 분석 서비스
> 최종 업데이트: 2026-03-05

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **목표** | 채용공고 + 기술 블로그 + 커뮤니티 데이터를 분석하여 기술 트렌드를 시각화 |
| **PRD** | `career/job-market-analysis-prd.md` (v3.0) |
| **Repo** | `job-market-insight/` |
| **Stack** | Spring Boot 3.4.3 + Java 21 (API) / Python 3.12 (Batch Container) / PostgreSQL 16 / React 19 + Recharts (Dashboard) |

---

## 2. 아키텍처

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│    React     │────▶│  Spring Boot API  │────▶│  PostgreSQL  │
│  Dashboard   │     │  /api/v1/         │     │  16 Alpine   │
│  (Recharts)  │     └──────────────────┘     └──────────────┘
└──────────────┘              ▲
                              │ DB Insert
                     ┌────────┴────────┐
                     │  Python Batch   │
                     │  Crawlers + NLP │
                     └─────────────────┘
```

### 디렉토리 구조
```
job-market-insight/
├── api/                          # Spring Boot REST API
│   ├── build.gradle              # Gradle 8.12, Spring Boot 3.4.3, Java 21
│   └── src/main/java/com/devpulse/
│       ├── DevPulseApplication.java
│       ├── posting/              # Controller + Service + DTO + Entity + Repository
│       ├── analysis/             # AnalysisController + AnalysisService + DTOs
│       ├── trend/                # TrendController + BuzzHiringGapService + Entities
│       ├── blog/                 # BlogTopicController + BlogTopicTrendService + Entities
│       ├── company/              # Company + CompanyCategory + CompanyRepository
│       ├── skill/                # Skill + SkillSourceScope + SkillRepository
│       └── global/               # GlobalExceptionHandler
├── batch/                        # Python 크롤러 + NLP + DB upsert
│   ├── Dockerfile                # 배치 컨테이너 이미지
│   ├── crawlers/
│   │   ├── base.py               # BaseCrawler ABC + RawJobPosting
│   │   ├── wanted.py             # 원티드 API 크롤러
│   │   ├── jumpit.py             # 점핏 JSON API 크롤러
│   │   ├── greenhouse.py         # Greenhouse Board API 크롤러 (쿠팡/두나무)
│   │   ├── tech_blog.py          # 테크 블로그 RSS 크롤러 (5개 회사)
│   │   └── trend/
│   │       ├── base.py           # TrendCrawler ABC + TrendPost
│   │       ├── geeknews.py       # GeekNews RSS 크롤러
│   │       ├── hackernews.py     # HackerNews Firebase API 크롤러
│   │       └── devto.py          # dev.to Forem API 크롤러
│   ├── nlp/
│   │   ├── skill_matcher.py      # 사전 기반 스킬 매칭
│   │   ├── normalizer.py         # 회사명/직무명 정규화
│   │   └── topic_extractor.py    # 블로그 주제 추출 (title/tags/content)
│   ├── report/
│   │   └── generator.py          # Markdown 리포트 자동 생성
│   ├── pipeline/
│   │   └── sync.py               # crawl 결과 DB upsert 파이프라인 + crawl_log 기록
│   ├── scheduler.py              # 컨테이너 내장 스케줄러 (6시간 주기)
│   ├── phase0_validate.py        # Phase 0 검증 파이프라인
│   └── tests/                    # pytest 121개
├── frontend/                     # React 19 대시보드
│   ├── src/pages/                # 7페이지 (스킬 랭킹, 회사 프로필, 포지션 비교, 갭 분석, 공고 검색, Buzz vs 채용, 블로그 트렌드)
│   ├── src/data/demo.ts          # 데모 데이터
│   ├── src/hooks/useChartStyles.ts  # 테마 반응형 차트 스타일
│   └── src/components/           # Layout, KpiCard 등
├── dashboard/                    # Streamlit 대시보드 (레거시)
│   ├── app.py
│   └── api_client.py
├── data/                         # 시드 데이터
│   ├── skills_seed.json          # 100개 스킬 (13 language, 21 framework, 10 DB, ...)
│   ├── companies_seed.json       # 29개 회사 (Big7 + 자회사 + 유니콘 + 스타트업)
│   ├── position_aliases.json     # BACKEND/PRODUCT/FDE 별칭
│   └── sample_postings.csv       # Phase 0 검증용 20건
├── docker-compose.yml            # postgres/api/frontend/scheduler + batch(profile, 수동)
├── .github/workflows/
│   ├── deploy.yml                # 서버 배포 + API health 대기
│   └── data-pipeline.yml         # 수동 긴급 배치 동기화 (workflow_dispatch)
└── CLAUDE.md                     # AI 활용 규칙 + 프로젝트 컨벤션
```

---

## 3. DB 스키마

### Flyway 마이그레이션: `V1__init_schema.sql`

**11 Tables**:
- `company` — 회사 정보 (category ENUM, JSONB tags/aliases)
- `job_posting` — 채용공고 (상태 생명주기: ACTIVE → CLOSED → EXPIRED → ARCHIVED)
- `skill` — 기술 스킬 (source_scope: JOB_POSTING/TREND/BOTH, keywords JSONB)
- `posting_skill` — 공고↔스킬 매핑 (is_required, is_preferred)
- `tech_blog_post` — 기술 블로그 글
- `blog_skill` — 블로그↔스킬 매핑
- `trend_post` — 커뮤니티 트렌드 글 (GeekNews 등)
- `trend_skill` — 트렌드↔스킬 매핑
- `unmatched_company` — 미매핑 회사명
- `crawl_log` — 크롤링 이력
- `analysis_snapshot` — 분석 결과 스냅샷

**8 ENUMs**: company_category, position_type, posting_status, skill_source_scope, trend_source, tech_blog_type, unmatched_status, crawl_status

---

## 4. REST API 엔드포인트

### 4.1 공고 조회
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/postings` | 필터링+페이징 (positionType, companyCategory, status, skillName, dateFrom/To) |
| GET | `/api/v1/postings/{id}` | 공고 상세 조회 |

### 4.2 분석
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/analysis/skill-ranking` | 스킬 랭킹 (positionType, companyCategory, includeClosedPostings, topN) |
| GET | `/api/v1/analysis/company-profile/{companyId}` | 회사 기술 프로필 (스킬 분포 + 포지션 분포) |
| GET | `/api/v1/analysis/position-comparison` | 포지션간 스킬 비교 (공통/고유 스킬 도출) |
| POST | `/api/v1/analysis/gap` | 갭 분석 (내 스킬 vs 시장 수요, 우선순위 분류) |

### 4.3 트렌드 분석
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/analysis/trend-ranking` | 트렌드 스킬 랭킹 (source, days, topN) |
| GET | `/api/v1/analysis/buzz-vs-hiring` | Buzz vs Hiring Gap 2×2 분류 (topN, days) |

### 4.4 블로그 토픽 분석
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/analysis/blog-topics/company/{companyId}` | 회사별 블로그 토픽 랭킹 (fromYear, toYear, topN) |
| GET | `/api/v1/analysis/blog-topics/yearly-trend` | 연도별 스킬 트렌드 (fromYear, toYear, topN) |
| GET | `/api/v1/analysis/blog-topics/skill/{skillName}` | 스킬별 회사 분포 (fromYear, toYear) |

### 4.5 에러 처리
- RFC 7807 ProblemDetail 형식
- 404: PostingNotFoundException, CompanyNotFoundException
- 400: IllegalArgumentException

### 예시 응답 — GET /api/v1/analysis/skill-ranking?positionType=BACKEND&topN=5
```json
{
  "snapshotDate": "2026-03-04",
  "totalPostings": 523,
  "positionType": "BACKEND",
  "rankings": [
    {"rank": 1, "skill": "Java", "count": 465, "percentage": 88.9, "requiredRatio": 0.76},
    {"rank": 2, "skill": "Spring Boot", "count": 429, "percentage": 82.0, "requiredRatio": 0.71},
    {"rank": 3, "skill": "AWS", "count": 351, "percentage": 67.1, "requiredRatio": 0.45}
  ]
}
```

---

## 5. 핵심 비즈니스 로직

### 5.1 SkillMatcher (사전 기반)
- 100개 스킬 사전 + 별칭 매핑
- **Longest-first matching**: "Spring Boot" 먼저 매칭 → "Spring" 중복 방지
- **한글 조사 경계 처리**: 영어 `(?<![a-zA-Z])`, 한글 `(?<![가-힣])` 분리
- **source_scope 필터링**: JOB_POSTING 분석 시 TREND 전용 키워드(vibe coding 등) 제외

### 5.2 딥 테크니컬 키워드 모델
- 각 기술(skill)에 `keywords` 필드로 심층 개념 키워드 관리
- 단순 기술명이 아닌, 해당 기술의 핵심 개념을 추적
- 예시: Redis → [캐싱 전략, 캐시 미스, 히트율, TTL, 캐시 무효화, pub/sub, 레디스 클러스터]
- **데이터 소스**: 테크 블로그 용어, 기술 면접 빈출 개념, 시스템 설계 토론
- **확장**: 기술 서적 첨부 → 키워드 자동 추출 (향후)

### 5.3 Gap Analysis 우선순위
| 상태 | 조건 | 우선순위 |
|------|------|----------|
| OWNED | 보유 스킬 | MAINTAINED |
| LEARNING | 학습 중 | CONTINUE |
| NOT_OWNED | rank ≤ 5 AND percentage ≥ 50% | CRITICAL |
| NOT_OWNED | rank ≤ 10 | HIGH |
| NOT_OWNED | rank ≤ 20 | MEDIUM |
| NOT_OWNED | rank > 20 | LOW |

### 5.4 데이터 파이프라인 아키텍처
```
┌─────────────────────────────────────────────────────┐
│  scheduler 컨테이너 (상시 실행, 6시간 주기)          │
│  scheduler.py → cmd_sync_all()                       │
│    ├── sync_job_postings (retry ×2, crawl_log 기록)  │
│    ├── sync_blog_posts   (retry ×2, crawl_log 기록)  │
│    └── sync_trend_posts  (retry ×2, crawl_log 기록)  │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────┐
│  PostgreSQL  │ ← crawl_log: 실행 이력/상태/소요시간
│  (공유 DB)   │ ← job_posting/tech_blog_post/trend_post
└──────────────┘
```
- **관측성**: 모든 크롤링 실행은 `crawl_log` 테이블에 기록 (source_type, status, duration_ms, items_collected)
- **장애 격리**: 크롤러별 독립 실행, 한 크롤러 실패가 다른 크롤러에 영향 없음
- **재시도**: 최대 2회 지수 백오프 (2초, 4초)
- **수동 실행**: GitHub Actions `workflow_dispatch` 또는 `docker compose --profile batch run --rm batch sync-all`

### 5.5 공고 생명주기
- ACTIVE → CLOSED (마감) → EXPIRED (만료) → ARCHIVED (보관)
- **절대 삭제 금지**: 시계열 분석을 위해 영구 보관

---

## 6. 테스트 현황

### 총 206개 테스트 통과 (Java 44 + Python 162)

#### Java (Spring Boot) — 44 tests
| 클래스 | 테스트 수 | 설명 |
|--------|-----------|------|
| PostingServiceTest | 6 | 필터 조회 (4) + 단건 조회/404 (2) |
| AnalysisServiceTest | 7 | 스킬 랭킹 (3) + 회사 프로필 (2) + 포지션 비교 (1) + 갭 분석 (1) |
| PostingControllerTest | 4 | MockMvc: 목록/필터/단건/404 |
| AnalysisControllerTest | 6 | MockMvc: 랭킹/회사/404/비교/갭/400 |
| BuzzHiringGapServiceTest | 6 | 트렌드 랭킹 (2) + 2×2 분류 (2) + 경계값 (2) |
| TrendControllerTest | 3 | MockMvc: 트렌드 랭킹/Buzz vs Hiring/기본 파라미터 |
| BlogTopicTrendServiceTest | 7 | 회사별 토픽 (4) + 연도별 트렌드 (2) + 스킬별 분포 (2) |
| BlogTopicControllerTest | 4 | MockMvc: 회사 토픽/연도 트렌드/스킬 분포/404 |
| DevPulseApplicationTest | 1 | contextLoads (Docker 조건부) |

#### Python (Batch) — 162 tests
| 모듈 | 테스트 수 | 설명 |
|------|-----------|------|
| test_skill_matcher | 18 | 기본 매칭, 복합 키워드, 중복 제거, 경계, scope, 엣지 케이스 |
| test_normalizer | 25 | 포지션 정규화 (14) + 회사명 정규화 (11) |
| test_phase0 | 10 | CSV 로딩, 스킬 추출, 빈도 분석, 리포트 생성 |
| test_wanted_crawler | 10 | 목록/상세/에러/풀 파이프라인/중복 제거 |
| test_geeknews_crawler | 8 | RSS 파싱, 날짜, 빈 피드, max_items, ID 추출 |
| test_jumpit_crawler | 9 | 목록/상세/에러/풀 파이프라인 |
| test_tech_blog_crawler | 8 | 초기화, RSS 파싱, 날짜, 태그, 콘텐츠, 빈 피드, 미등록 회사 |
| test_topic_extractor | 9 | 단일/복수/없음 토픽, 태그 추출, 중복 제거, 콘텐츠 추출 |
| test_greenhouse_crawler | 12 | 초기화, 목록 조회, 빈 보드, API 에러, 상세, HTML 제거, 풀 파이프라인, 멀티 보드 |
| test_report_generator | 12 | 마크다운 생성, 섹션별 검증, 파일 저장, 빈 데이터, 부분 데이터 |
| test_hackernews_crawler | 20 | 초기화, fetch, item 변환, 풀 파이프라인, rate limit |
| test_devto_crawler | 21 | 초기화, fetch, article 변환, ISO 8601 파싱, 풀 파이프라인 |

---

## 7. 설계 결정 (ADR)

### ADR-001: Polyglot Architecture
- **결정**: API는 Java/Spring Boot, 배치는 Python
- **이유**: Spring Boot는 복잡한 쿼리/트랜잭션에 강하고, Python은 크롤링/NLP 생태계 활용

### ADR-002: PostgreSQL 단일 DB
- **결정**: PostgreSQL 16 + JSONB
- **이유**: JSONB로 태그/별칭 저장, 별도 NoSQL 불필요

### ADR-003: Dictionary Matching First
- **결정**: Phase 1은 사전 기반 매칭만 사용 (ML/AI 없음)
- **이유**: 100개 사전으로도 90%+ 커버리지, Phase 0 검증으로 확인

### ADR-004: TDD Mandatory
- **결정**: 모든 기능은 테스트 코드가 성공 기준
- **이유**: 안정적인 리팩토링, Phase 전환 시 안전망

### ADR-005: Package-by-Feature
- **결정**: Spring Boot 패키지 구조를 layer 기반(api/domain/service)에서 feature 기반(posting/analysis/trend/blog)으로 전환
- **이유**: Controller+Service+DTO+Entity를 같은 패키지에 배치하면 feature 경계가 명확하고, 패키지 접근 제한(package-private) 활용 가능

### ADR-006: Job Posting Archival
- **결정**: 공고는 절대 삭제하지 않음 (ACTIVE→CLOSED→EXPIRED→ARCHIVED)
- **이유**: 시계열 분석, 히스토리컬 트렌드 파악

---

## 8. 진행 타임라인

### Phase 0: 검증 ✅
- [x] 프로젝트 초기화 + 스캐폴딩
- [x] Flyway 마이그레이션 (11 tables)
- [x] 시드 데이터 (skills 100, companies 29, positions 3)
- [x] SkillMatcher + Normalizer + 43 tests
- [x] Phase 0 검증 파이프라인 + 리포트

### Phase 1 Week 1: 인프라 + 크롤러 ✅
- [x] 원티드 API 크롤러 + 10 tests
- [x] Spring Boot Entity/Repository (5 entities, 4 repositories)

### Phase 1 Week 2: REST API + Dashboard ✅
- [x] DTO Records (7개)
- [x] PostingService + PostingController (10 tests)
- [x] AnalysisService + AnalysisController (13 tests)
- [x] Streamlit 대시보드 (5페이지, 데모 모드)

### Phase 2 Week 3: 크롤러 확장 + Trend ✅
- [x] GeekNews RSS 크롤러 (feedparser, 8 tests)
- [x] Jumpit 크롤러 (내부 JSON API, 9 tests)
- [x] TrendPost + TrendSkill JPA Entity + Repository
- [x] BuzzHiringGapService (2×2 분류 + 5 tests)
- [x] TrendController (trend-ranking, buzz-vs-hiring + 3 tests)
- [x] TechBlogCrawler (RSS 기반, 5개 회사 + 8 tests)
- [x] TopicExtractor (title/tags/content 추출 + 9 tests)
- [x] TechBlogPost + BlogSkill JPA Entity + Repository
- [ ] Greenhouse 크롤러 (쿠팡, 두나무)

### Phase 2 Week 4: 분석 고도화 ✅
- [x] BlogTopicTrendService (회사별 토픽, 연도별 트렌드, 스킬별 분포 + 7 tests)
- [x] BlogTopicController (3 endpoints + 4 tests)
- [x] GlobalExceptionHandler — IllegalArgumentException 핸들러 추가
- [x] Greenhouse 크롤러 (쿠팡/두나무 Board API + 12 tests)
- [x] 리포트 자동 생성 (report/generator.py + 12 tests)

### Phase 3 Week 5: 리팩토링 + 크롤러 + React ✅
- [x] 백엔드 Package-by-Feature 리팩토링 (52 files → 7 feature packages)
- [x] HackerNews Firebase API 크롤러 (hackernews.py + 20 tests)
- [x] dev.to Forem API 크롤러 (devto.py + 21 tests)
- [x] React 대시보드 7페이지 (Vite + Recharts + TailwindCSS 4 + framer-motion)
- [x] **테스트 206개 통과** (Java 44 + Python 162)

### 운영 자동화 (2026-03-05)
- [x] 배포 워크플로우 고도화 (`deploy.yml`: container health 기준)
- [x] 배치 업서트 파이프라인 (`sync-all`: jobs/blogs/trends)

### 데이터 파이프라인 확장 (2026-03-05)
- [x] 딥 테크니컬 키워드 모델: 105개 스킬에 심층 개념 키워드 추가
- [x] Flyway V2 마이그레이션: skill 테이블에 keywords 컬럼 추가
- [x] crawl_log 기록: 모든 sync 실행마다 실행 이력 기록
- [x] 크롤러별 재시도 로직 (지수 백오프 ×2)
- [x] 컨테이너 내장 스케줄러 (scheduler.py, 6시간 주기)
- [x] GitHub Actions cron → workflow_dispatch 전용

---

## 9. 실행 방법

### 사전 요구사항
- Java 21, Python 3.10+, Docker, Gradle 8.12+

### DB 실행
```bash
cd job-market-insight
docker compose up -d
```

### API 서버
```bash
cd api
./gradlew bootRun
# http://localhost:8080/api/v1/postings
```

### 배치 테스트
```bash
cd batch
pip install -r requirements.txt  # pytest, responses, pandas
python -m pytest -v
```

### 배치 동기화 실행 (로컬)
```bash
docker compose up -d postgres
docker compose --profile batch build batch
docker compose --profile batch run --rm batch sync-all
```

### 대시보드
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
# http://localhost:8501
```

---

## 10. 주요 버그/이슈 이력

| 날짜 | 이슈 | 원인 | 해결 |
|------|------|------|------|
| 03-03 | 한글 조사 경계 버그 | `(?<![a-zA-Z가-힣])` 패턴이 "Java와"에서 실패 | 영어/한글 경계 패턴 분리 |
| 03-04 | List.of() varargs 모호성 | `List.of(new Object[]{})` 타입 추론 실패 | `List.<Object[]>of()` 명시 |
| 03-04 | contextLoads Docker 의존 | Testcontainers 없이 @SpringBootTest 실패 | `@EnabledIf("isDockerAvailable")` |
| 03-04 | 갭 분석 CRITICAL 조건 | 테스트 데이터 percentage < 50% | 테스트 데이터 수정 (40→60) |
| 03-04 | GeekNews published_parsed | hasattr가 dict key에 False 반환 | entry.get("published_parsed")로 변경 |
| 03-04 | TopicExtractor dict 접근 | SkillMatcher가 MatchedSkill dataclass 반환 | m["name"] → m.skill_name 수정 |
| 03-04 | SkillMatcher 리스트 초기화 | __init__이 path만 허용, list 불가 | isinstance 분기로 list/path 모두 지원 |
| 03-04 | Package-by-feature sed 실패 | `find -path '*/api/*' -prune`이 프로젝트 디렉토리 `api/` 자체를 prune | prune 제거, 전체 .java에 sed 적용 |
| 03-05 | position-comparison 400 | 프론트 `get()`가 기존 query string에 `?`를 중복 결합 | API client 경로 조립 로직 수정 |
| 03-05 | company-profile 404 | 회사 ID 하드코딩과 운영 DB ID 불일치 | 이름 기반 조회 엔드포인트 추가 + 프론트 변경 |
| 03-05 | gap 화면 공백 | `gaps=[]`인 정상 응답에 대한 빈 상태 UI 부재 | 빈 데이터 안내 컴포넌트 렌더링 추가 |
