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
