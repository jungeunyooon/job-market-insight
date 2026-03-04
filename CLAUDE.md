# DevPulse - AI Agent Instructions

## Project Overview
DevPulse: 개발자 채용시장 분석 서비스
- Spring Boot 3.x + Java 21 (API) + Python (batch crawling/NLP)
- PostgreSQL, Docker, Flyway, QueryDSL, Testcontainers

## PRD Location
- `/Users/jungeun/Documents/career/job-market-analysis-prd.md` (v3.0, source of truth)

## Development Rules

### TDD (Test-Driven Development) — 최우선 원칙
- **모든 작업의 성공 기준은 테스트 코드다**
- Red → Green → Refactor 순서 엄수
- 테스트 없는 코드는 완료가 아니다
- Spring Boot: JUnit 5 + Mockito (단위), Testcontainers (통합), MockMvc (API)
- Python: pytest + responses (HTTP mock), Testcontainers (E2E)

### Git Workflow
- `main` 브랜치: 안정 코드만
- Feature 브랜치: `feature/{domain}/{task}` (예: `feature/api/posting-crud`)
- 커밋 메시지: 한국어 OK, conventional commits 스타일
- git worktree로 병렬 작업 시 충돌 최소화를 위해 도메인별 분리

### Code Conventions
- Java: Google Java Style, record for DTOs
- Python: Black formatter, type hints 필수
- 모든 API는 `/api/v1/` prefix
- Entity는 `domain/{도메인명}/` 패키지
- 한국어 주석 OK (공고, 크롤러 등 도메인 특화 용어)

### Architecture Decisions
- Phase 1: Dictionary matching ONLY (Kiwi/TF-IDF는 Phase 2/3)
- 공고 영구 보관 (절대 삭제 금지)
- source_scope (JOB_POSTING/TREND/BOTH)로 키워드 오염 방지
- ai_ml → ai_ml_model + ai_ml_devtool 분리
- "bare AI" 단독 매칭 금지 (복합어 패턴만)

### Documentation
- 작업 진행 상황: `/docs/PROGRESS.md`에 기록
- 주요 기술적 의사결정: `/docs/DECISIONS.md`에 기록
- 각 Phase 완료 시 log 업데이트

## Project Structure
```
devpulse/
├── docker-compose.yml          # PostgreSQL
├── api/                        # Spring Boot 3.x + Java 21
│   ├── build.gradle
│   └── src/main/java/com/devpulse/
│       ├── domain/{company,posting,skill,blog,trend,analysis}/
│       ├── api/                # Controllers + DTOs
│       ├── service/            # Business logic
│       └── scheduler/          # @Scheduled
├── batch/                      # Python (crawling + NLP)
│   ├── crawlers/               # BaseCrawler implementations
│   ├── nlp/                    # skill_matcher, normalizer
│   └── tests/
├── data/                       # Seed data (JSON)
│   ├── skills_seed.json
│   ├── companies_seed.json
│   └── position_aliases.json
└── docs/
```

## Build & Run
```bash
# Infrastructure
docker-compose up -d  # PostgreSQL

# API (Spring Boot)
cd api && ./gradlew bootRun

# Batch (Python)
cd batch && pip install -r requirements.txt && python main.py

# Tests
cd api && ./gradlew test
cd batch && pytest
```

## AI 활용 규칙 (서비스 특화)

### 작업 완료 시 필수 체크리스트
1. **테스트 통과 확인**: 모든 관련 테스트가 통과하는지 `pytest` / `./gradlew test` 실행
2. **log.md 업데이트**: `/Users/jungeun/Documents/career/log.md`에 작업 내용, 버그 수정, AI 활용 내역 기록
3. **PROGRESS.md 업데이트**: 체크리스트 항목 완료 표시
4. **CLAUDE.md 업데이트**: 새로운 아키텍처 결정이나 패턴 발견 시 반영

### AI 에이전트 작업 원칙
- **PRD가 source of truth**: 구현 전 반드시 PRD의 해당 섹션 확인
- **테스트 먼저**: 구현 코드보다 테스트 코드를 먼저 작성 (Red → Green → Refactor)
- **한글 조사 주의**: 한국어 텍스트 처리 시 조사(와/과/을/를/이/가 등) 경계 문제 항상 고려
- **시드 데이터 검증**: skills_seed.json, companies_seed.json 변경 시 관련 테스트 재실행
- **scope 오염 방지**: TREND-only 키워드가 채용 분석에 섞이지 않도록 source_scope 필터 필수 적용
- **커밋 전 확인**: `cd batch && python -m pytest tests/ -v` && `cd api && ./gradlew test`

### 크롤링 관련 AI 활용 제한
- 크롤러 구현 시 robots.txt 준수 코드 필수 포함
- Rate limit (1 req/sec) 하드코딩
- 개인정보 마스킹 로직 크롤링 시점에 반드시 적용
- 크롤러 테스트는 HTTP mock (responses 라이브러리) 사용, 실제 사이트 요청 금지

### 한국어 NLP 처리 주의사항
- 영어 키워드 경계: `(?<![a-zA-Z])` — 한글 조사가 붙어도 매칭되도록
- 한글 키워드 경계: `(?<![가-힣])` — 한글 복합어 내부 오매칭 방지
- "bare AI" 패턴 등록 금지 — 반드시 복합어 패턴만 사용
- aliases 추가 시 기존 테스트 재실행하여 부작용 확인

## Key Domain Terms (Korean)
- 채용 공고 = Job Posting
- 지원서 = Application
- 기술 사전 = Skill Dictionary
- 크롤러 = Crawler
- 공고 마감 = Posting Closed
- 빈도 분석 = Frequency Analysis
- 갭 분석 = Gap Analysis
- 트렌드 분석 = Trend Analysis (Buzz vs Hiring Gap)
- 블로그 주제 트렌드 = Blog Topic Trend
