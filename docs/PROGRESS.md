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
- [ ] Docker Compose 배포
- [ ] CI/CD
- [ ] 기술 블로그 시리즈
