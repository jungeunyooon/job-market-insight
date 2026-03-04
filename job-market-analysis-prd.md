# 취업시장 분석 서비스 PRD (Product Requirements Document)

> **프로젝트명**: DevPulse (개발자 채용시장 맥박)
> **작성일**: 2026-03-04
> **작성자**: 윤정은
> **버전**: v3.0 (2차 비판 반영 + AI/바이브 코딩 트렌드 통합)
> **상태**: Draft

---

## 1. 프로젝트 개요

### 1.1 문제 정의

신입 개발자의 취업 준비는 **"감"에 의존**한다.

- "요즘 Kafka가 많이 나온다더라" → 근거는?
- "Spring Boot를 하면 되겠지" → 어떤 수준까지?
- "쿠팡은 Java 쓴다던데" → 실제 공고에서 어떤 스택을 요구하는가?
- "테크 블로그 읽으면 도움된다" → 어떤 블로그에서 어떤 키워드가 핵심인가?

채용 시장에 대한 **데이터 기반 분석**이 없으면:
1. 불필요한 기술을 공부하는 데 시간을 낭비한다
2. 실제 시장이 요구하는 역량과 내 준비 사이의 갭을 모른다
3. 회사별/포지션별로 다른 요구사항을 파악하지 못한다

### 1.2 해결 방안

**채용 공고 + 테크 블로그**를 수집·분석하여, 신입 개발자가 **데이터 기반으로 취업 전략**을 수립할 수 있는 도구를 구축한다.

```
[Python 배치]                      [Spring Boot API]
채용 공고 크롤링 ─┐                       │
                  ├→ 키워드 추출 → DB ←──→ REST API → 대시보드
테크 블로그 크롤링 ─┘                       │
```

### 1.3 왜 이 프로젝트를 하는가 (의도)

**1차 목적**: 내가 취업 준비에 활용할 데이터 기반 전략 도구
**2차 목적**: 이력서에 적었을 때 반박 여지가 없는 프로젝트

이 프로젝트가 이력서에서 증명하는 것:
- **백엔드 설계 능력**: Spring Boot API 서버 설계 + 다국어(Java/Python) 시스템 통합
- **데이터 파이프라인**: 크롤링 → 전처리 → 분석의 배치 처리 설계
- **문제 해결 사고**: "감" → "데이터"로 전환하는 엔지니어링 접근
- **적정 기술 판단**: 문제 크기에 맞는 도구 선택 (과잉 설계 회피)

### 1.4 타겟 사용자

**Primary**: 나 자신 (신입 백엔드 개발자 취준생)
**Secondary**: 동일 상황의 주니어 개발자 취준생

### 1.5 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 수집된 채용 공고 수 | Phase 1: 500건+, 6개월 누적: 5,000건+ (영구 보관) | DB 레코드 수 |
| 수집된 테크 블로그 글 수 | Phase 1: 300건+, 6개월 누적: 1,000건+ | DB 레코드 수 |
| 키워드 추출 정확도 | 수동 검증 50건 대비 precision >= 0.85 **(목표, Phase 1 완료 후 측정)** | 사전 매칭 기준 |
| 실제 인사이트 산출 | "이 분석으로 학습 우선순위를 변경했다"는 구체적 사례 1건 이상 | 분석 결과 문서화 |
| 분석 리포트 | 회사별 + 포지션별 스냅샷 리포트 | Markdown 자동 생성 |

### 1.6 이 프로젝트의 범위와 솔직한 포지셔닝

**이 프로젝트가 하는 것**:
- 채용 공고를 **최대한 많이, 지속적으로** 수집하고 영구 보관한다. 초기 500건이 아니라, 매주 누적되어 수천~수만 건으로 성장하는 구조다.
- 배치 수집 → 분석 → 리포트 생성 → **서비스로 배포**한다. 개인 도구로 시작하지만 배포하여 다른 취준생도 사용할 수 있게 한다.
- 사전 기반 매칭이 핵심이고, NLP 모델(Kiwi, TF-IDF)은 사전 커버리지를 보완하는 보조다.

**이 프로젝트가 아닌 것**:
- 실시간 서비스가 아니다. 배치 수집 주기(주 2~3회)로 동작하며, 실시간 공고 알림은 범위 밖이다.
- 딥러닝/LLM 기반 분석이 아니다. BERT나 GPT로 키워드를 추출하지 않는다. 기술 키워드는 영어 고유명사이므로 **사전 매칭이 더 정확하고 설명 가능**하다.
- 채용 추천/매칭 서비스가 아니다. "이 공고에 지원하세요"가 아니라 "시장이 이런 기술을 요구합니다"를 보여주는 분석 도구다.

> **왜 이 구분을 적는가**: 면접에서 "이건 엑셀로도 할 수 있지 않나?"라는 질문에 대한 답변 — "맞습니다. Phase 0에서 실제로 CSV + 스크립트로 시작했습니다. 하지만 데이터가 수천 건으로 쌓이고 반복 분석이 필요해지면서 구조화가 필요했고, 다른 취준생도 쓸 수 있게 배포하려면 API 서버가 필요했습니다. 그 **성장 과정에서의 기술적 의사결정**이 이 프로젝트의 핵심입니다."

---

## 2. 관련 프로젝트 조사 결과

### 2.1 국내 오픈소스

| 프로젝트 | 핵심 기능 | 참고할 점 | 한계 |
|----------|----------|----------|------|
| [heehehe/job-trend](https://github.com/heehehe/job-trend) | 사람인 크롤링 → 기술스택 시각화 (Sankey, Sunburst) | BigQuery 파이프라인, 직무-기술 매핑 시각화 | 사람인 단일 소스 |
| [Pseudo-Lab/JobPT](https://github.com/Pseudo-Lab/JobPT) | JD-이력서 매칭 시스템 | JD 스킬 추출 → 매칭 파이프라인 | 매칭 정확도 미검증 |
| [jojoldu/junior-recruit-scheduler](https://github.com/jojoldu/junior-recruit-scheduler) | 주니어 채용 정보 집약 (3.6k star) | 데이터 소스 목록 | 수동 업데이트, 분석 기능 없음 |
| [lovit/KR-WordRank](https://github.com/lovit/KR-WordRank) | 한국어 비지도 키워드 추출 | 형태소 분석 없이 한국어 키워드 추출 | 키프레이즈 추출 약함 |
| [lovit/soynlp](https://github.com/lovit/soynlp) | 한국어 NLP (신조어 탐지) | 기술 용어 등 사전에 없는 단어 추출 | 범용 NLP 대비 기능 제한 |

### 2.2 해외 서비스/프로젝트

| 서비스 | 핵심 기능 | 참고할 점 |
|--------|----------|----------|
| [Levels.fyi](https://levels.fyi) | 테크 기업 레벨별 보상 비교 | 데이터 검증 시스템, 직관적 비교 UX |
| LinkedIn Talent Insights | 800M+ 프로필 기반 스킬 수요/공급 분석 | 스킬 수요/공급 분석 모델 |
| [PaulMcInnis/JobFunnel](https://github.com/PaulMcInnis/JobFunnel) | 다중 채용사이트 스크래핑 → 통합 | 확장 가능한 스크래퍼 아키텍처, 딜레이 알고리즘 |
| [schmcklr/skill_extractor](https://github.com/schmcklr/skill_extractor) | JD → 스킬 추출 → 시계열 트렌드 | Dynamic Topic Modeling, 시계열 분석 |

### 2.3 기존 프로젝트와의 차별화

| 기존 프로젝트 | DevPulse 차별점 |
|--------------|----------------|
| 단일 플랫폼 크롤링 | **다중 소스** (채용 플랫폼 + 회사 직접 + 테크 블로그) |
| Python 스크립트 단독 | **Spring Boot API + Python 배치 분리** (백엔드 설계 역량 증명) |
| 전체 직군 대상 | **특정 포지션 특화** (BE, PE, FDE) + 타겟 회사 집중 |
| 빈도 분석만 | **블로그 참조 분석** + **스킬 보유/미보유 갭 분석** |
| 영어 전용 NLP | **한국어 기술 용어 정규화 사전** (한/영 혼용 처리) |

---

## 3. 데이터 수집 전략

### 3.1 타겟 포지션

| 포지션 | 검색 키워드 (한/영) | 비고 |
|--------|-------------------|------|
| Backend Engineer | "백엔드", "서버 개발자", "Backend Engineer", "Server Developer", "Platform Engineer (Backend)" | 핵심 타겟 |
| Product Engineer | "프로덕트 엔지니어", "Product Engineer", "풀스택", "Full-stack" | 회사마다 정의 다름 |
| Forward Deployed Engineer | "FDE", "Solutions Engineer", "Technical Consultant" | 한국 시장에서 희귀. 토스, 센드버드 등 일부에서 사용. 수집 결과가 적으면 분석 제외 |

> **직무명 정규화 필수**: "서버 개발자" = "백엔드 엔지니어" = "Backend Engineer". 정규화 매핑 사전 구축.

### 3.2 타겟 회사

#### 회사 카테고리 분류

사용자가 분석 시 회사 규모/유형별로 필터링할 수 있도록 카테고리를 분류한다.

| 카테고리 | 정의 | 예시 |
|---------|------|------|
| `BIGTECH` | 국내 IT 대기업 (시총 상위, 개발자 1,000명+) | 네이버, 쿠팡, 카카오, 라인, 배민, 토스, 당근 |
| `BIGTECH_SUB` | 대기업 자회사/계열사 | 카카오페이, 카카오뱅크, 네이버클라우드, 네이버파이낸셜, 라인플러스 |
| `UNICORN` | 유니콘 스타트업 (기업가치 $1B+) | 야놀자, 직방, 리디, 뱅크샐러드, 컬리, 무신사, 두나무, 오늘의집 |
| `STARTUP` | 성장 스타트업 (시리즈 A~C, 개발자 50명+) | 센드버드, 채널톡, 토스랩, 그린랩스, 버킷플레이스 |
| `SI` | SI/솔루션 기업 | 삼성SDS, LG CNS, SK C&C, NHN |
| `MID` | 중견 IT 기업 | NHN, 한글과컴퓨터, 카페24, 드림어스컴퍼니 |
| `FINANCE` | 금융/핀테크 | 카카오뱅크, 토스, KB데이타시스템, 신한DS |

> **분류 원칙**: 한 회사가 여러 카테고리에 해당하면 **가장 특화된 카테고리**를 부여한다 (예: 카카오뱅크 → BIGTECH_SUB + FINANCE 중 BIGTECH_SUB 우선, FINANCE는 태그로 보조). 카테고리는 `company` 테이블의 `category` 필드, 보조 태그는 `tags (JSONB)` 필드로 관리한다.

#### Big 7 (빅테크: `BIGTECH`)

| 회사 | 채용 페이지 | 테크 블로그 | 크롤링 방식 |
|------|-----------|-----------|-----------|
| 네이버 | recruit.navercorp.com | d2.naver.com | SPA → Headless Browser |
| 쿠팡 | coupang.jobs/kr | medium.com/coupang-engineering | Greenhouse ATS → Board API |
| 카카오 | careers.kakao.com | tech.kakao.com/blog | Custom |
| 라인 | careers.linecorp.com | engineering.linecorp.com | LY Corporation 재편 주의 |
| 배민 (우아한형제들) | career.woowahan.com | techblog.woowahan.com | Custom + RSS 가능 |
| 토스 (비바리퍼블리카) | toss.im/career/jobs | toss.tech | Next.js SSR → HTML 파싱 |
| 당근 | team.daangn.com/jobs | medium.com/daangn | Custom + Medium RSS |

#### 대기업 자회사 (`BIGTECH_SUB`)

| 회사 | 채용 페이지 | 크롤링 방식 | 비고 |
|------|-----------|-----------|------|
| 카카오페이 | careers.kakaopay.com | Custom | 핀테크 |
| 카카오뱅크 | careers.kakaobank.com | Custom | 금융 |
| 네이버클라우드 | recruit.navercorp.com (통합) | 네이버와 동일 | 클라우드 |
| 네이버파이낸셜 | recruit.navercorp.com (통합) | 네이버와 동일 | 핀테크 |
| 라인플러스 | careers.linecorp.com (통합) | 라인과 동일 | 글로벌 |

#### 유니콘 스타트업 (`UNICORN`)

| 회사 | 채용 페이지 | 테크 블로그 | ATS |
|------|-----------|-----------|-----|
| 야놀자 | careers.yanolja.co | medium.com/yanolja | Custom |
| 직방 | career.zigbang.com | medium.com/zigbang | Custom |
| 리디 | ridi.career.greetinghr.com | ridicorp.com/story-category/tech-blog | GreetingHR |
| 뱅크샐러드 | corp.banksalad.com/jobs | blog.banksalad.com/tech | Custom |
| 컬리 | kurly.career.greetinghr.com | helloworld.kurly.com | GreetingHR |
| 무신사 | musinsacareers.com (자체 이전 확인 필요) | medium.com/musinsa-tech | 자체/GreetingHR 혼용 |
| 두나무 | careers.dunamu.com | (미확인) | Greenhouse |
| 오늘의집 | bucketplace.com/careers | (비공개) | Custom |

#### 성장 스타트업 (`STARTUP`)

| 회사 | 채용 페이지 | ATS | 비고 |
|------|-----------|-----|------|
| 센드버드 | sendbird.com/ko/careers | Custom | 글로벌 SaaS |
| 채널톡 | channel.io/ko/jobs | Custom | B2B SaaS |
| 토스랩 (잔디) | tosslab.com/careers | Custom | 협업 도구 |
| 그린랩스 | greenlabs.co.kr/careers | Custom | 애그리테크 |

#### SI/중견 (`SI`, `MID`) — Phase 2 확장

| 회사 | 카테고리 | 채용 페이지 | 비고 |
|------|---------|-----------|------|
| 삼성SDS | SI | samsungsds.com/kr/careers | 대형 SI |
| LG CNS | SI | lgcns.com/careers | 대형 SI |
| NHN | MID | recruit.nhn.com | 게임/클라우드/커머스 |
| 카페24 | MID | cafe24corp.com/recruit | 이커머스 플랫폼 |

> **Phase 2 확장 전략**: Phase 1은 원티드/점핏 플랫폼 + Big 7/유니콘 직접 크롤링. Phase 2에서 자회사, 스타트업, SI/중견 대상을 원티드/점핏 검색 결과로 확장. 개별 회사 채용 페이지 크롤러는 **공고 수가 10건 이상인 회사만** 별도 구현 (ROI 판단).

> **URL 검증 필수**: 모든 URL은 구현 전에 직접 브라우저로 접속하여 검증한다. ATS 이전(예: 무신사 GreetingHR → 자체 사이트)이 있을 수 있다.

### 3.2.1 채용 플랫폼을 통한 카테고리 확장

원티드/점핏에서 검색하면 Big 7/유니콘 외에도 다양한 회사의 공고가 수집된다. 이들을 자동으로 카테고리 분류하는 전략:

```
[Step 1] 원티드/점핏 크롤링 → 회사명 추출
[Step 2] company 테이블에 이미 등록된 회사? → 해당 카테고리 사용
[Step 3] 미등록 회사? → unmatched_company 테이블에 저장
[Step 4] 주기적으로 unmatched_company 검토 → company 테이블에 카테고리와 함께 등록
```

> **자동 분류는 하지 않는다**: 회사 카테고리는 주관적 판단이 필요하다 (예: "이 회사가 유니콘인가 스타트업인가?"). 최초 시드 데이터(Big 7 + 유니콘)는 수동 등록하고, 이후 새로 발견되는 회사는 미분류 상태로 저장한 뒤 수동 분류한다.

### 3.3 채용 플랫폼

| 플랫폼 | API | 접근성 | 우선순위 |
|--------|-----|-------|---------|
| **원티드** | ✅ [OpenAPI](https://openapi.wanted.jobs/) | Key 신청 필요 | **1순위** (IT 특화, 구조화된 데이터) |
| **점핏** | ❌ (내부 JSON API) | 공개 페이지 XHR 파싱 | **2순위** (개발자 특화, 기술스택 태그) |
| **사람인** | ✅ [공식 API](https://oapi.saramin.co.kr/) | 기관 우선, 개인 승인 불확실. 500콜/일 | 3순위 (승인 실패 시 제외) |
| ~~잡코리아~~ | - | **제외** | 사람인-잡코리아 120억 손배 판례. 봇 탐지 공격적. |
| ~~프로그래머스~~ | - | **제외** | 2025.06.23 채용 서비스 종료 |
| ~~LinkedIn~~ | - | **제외** | Proxycurl $500K 판결. 공식 API는 파트너 전용 |

> **사람인 API 리스크**: 개인 개발자에게 승인 안 될 가능성 높음. **fallback**: 원티드 + 점핏 + 회사 직접 크롤링으로 충분한 데이터 확보 가능.

### 3.4 테크 블로그

**수집 방식**: RSS 피드 우선 → HTML 파싱 fallback
**수집 범위**: 최신 글뿐 아니라 **과거 아카이브 전체**를 크롤링하여 연도별 주제 트렌드 분석에 활용

| 회사 | 블로그 URL | 방식 | 예상 글 수 |
|------|-----------|------|-----------|
| 네이버 D2 | d2.naver.com | RSS + 아카이브 HTML 파싱 | 500+ (2015~) |
| 쿠팡 | medium.com/coupang-engineering | Medium RSS + Archive | 100+ (2020~) |
| 카카오 | tech.kakao.com/blog | HTML 파싱 (페이지네이션) | 400+ (2016~) |
| 배민 | techblog.woowahan.com | RSS (WordPress) + 아카이브 | 300+ (2017~) |
| 토스 | toss.tech | HTML 파싱 (페이지네이션) | 200+ (2020~) |
| 당근 | medium.com/daangn | Medium RSS + Archive | 150+ (2019~) |
| 뱅크샐러드 | blog.banksalad.com/tech | HTML 파싱 | 100+ (2018~) |
| 컬리 | helloworld.kurly.com | HTML 파싱 | 100+ (2019~) |
| 무신사 | medium.com/musinsa-tech | Medium RSS + Archive | 50+ (2021~) |
| 라인 | engineering.linecorp.com | HTML 파싱 | 300+ (2016~) |
| 리디 | ridicorp.com/story-category/tech-blog | HTML 파싱 | 50+ (2019~) |

**아카이브 크롤링 전략**:
```
[Phase 1] 최초 1회: 전체 아카이브 크롤링 (2015~ 현재)
  • 블로그별 페이지네이션 / 아카이브 페이지 순회
  • 각 글: title, url, published_at, content_text 수집
  • Rate limit 엄수 (1 req/sec). 전체 크롤링에 수 시간 소요 예상

[이후] 주 1회: 신규 글만 수집 (published_at > last_crawled_at)
  • RSS 피드로 신규 감지 → 본문은 HTML 파싱으로 수집
```

> **왜 아카이브 전체를 크롤링하는가**: "2020년에 배민은 MSA 전환을 집중적으로 다뤘고, 2023년부터 Kotlin 비중이 급증했다"는 인사이트는 **과거 데이터 없이 불가능**하다. 연도별 주제 트렌드는 이 프로젝트의 핵심 차별화 기능이며, 채용 공고의 키워드 트렌드와 교차하면 "회사가 블로그에서 어떤 기술을 이야기한 후 1~2년 뒤에 채용에 반영한다"는 패턴을 발견할 수 있다.

> Medium RSS 검증: `https://medium.com/feed/{publication}` 형식으로 접근 가능 여부 구현 전 확인. Medium 아카이브는 `/{publication}/archive/{year}/{month}` 페이지네이션.

### 3.5 LinkedIn 전략

**결론: 직접 수집 제외.**
- 법적 리스크 극도로 높음 (Proxycurl 종료 판결, hiQ Labs 합의)
- 대안: 주요 회사 개발자 프로필 기술 키워드를 수동 샘플링(10~20건)하여 별도 참고 데이터로 활용

### 3.6 기술 트렌드 소스 (Buzz 데이터)

**목적**: 채용 공고가 "회사가 실제로 요구하는 것"이라면, 기술 뉴스/커뮤니티는 "업계가 이야기하는 것"이다. 이 둘의 **Gap**을 정량화하는 것이 핵심 가치다.

| 소스 | URL | 접근 방식 | 우선순위 | 비고 |
|------|-----|----------|---------|------|
| **GeekNews** | news.hada.io | RSS (`/rss/news`) | **1순위** | 한국 기술 커뮤니티. HN 요약 포함. 한국 시장 맥락 |
| **Hacker News** | news.ycombinator.com | Firebase API (무료, 무제한) | 2순위 (Phase 2) | 글로벌 트렌드. GeekNews와 중복 가능 |
| **dev.to** | dev.to | Forem API (무료) | 3순위 (Phase 2) | 개발자 커뮤니티 실전 관점 |
| ~~Twitter/X~~ | - | **제외** | - | Free tier 500 posts/월. Basic $100/월. 비용 대비 가치 없음 |
| ~~LinkedIn 포스트~~ | - | **제외** | - | 공개 피드 API 없음. 법적 리스크 |
| ~~Reddit~~ | - | **Phase 3 검토** | - | 2023 API 유료화 ($0.24/1K calls). RSS fallback 가능 |

> **왜 GeekNews가 1순위인가**: (1) RSS 피드 공개. (2) 한국어 맥락으로 큐레이션됨. (3) HN의 주요 글을 한국어 요약으로 제공하므로, GeekNews만 수집해도 글로벌 + 한국 트렌드를 동시에 커버. (4) Phase 2에서 HN 원본을 추가하면 커버리지 확장 가능.

> **감성 분석은 전 Phase에서 제외한다**: 뉴스 제목에 대한 감성 분석은 미해결 NLP 문제다. "React 보안 취약점 발견"은 부정적이지만 React 채용에 영향을 주지 않는다. 빈도만으로 충분하고, 감성은 actionable insight를 주지 않는다. 면접에서 이 판단을 먼저 말하면 "적정 기술 선택"을 보여줄 수 있다.

---

## 4. 시스템 아키텍처

### 4.1 핵심 설계 원칙: 점진적 성장 (Evolutionary Architecture)

**이 프로젝트는 "처음부터 완벽한 시스템"이 아니라, "데이터가 늘어나면서 구조가 성장하는 시스템"이다.**

```
Phase 0 (검증):  Python 스크립트 + CSV → "이걸로 유용한 인사이트가 나오는가?" 검증
Phase 1 (구조화): PostgreSQL + Spring Boot API → 반복 분석이 필요해진 시점에서 구조화
Phase 2 (확장):  크롤러 추가 + 분석 고도화 → 데이터가 충분해진 시점에서 고급 분석
Phase 3 (서비스): React 대시보드 → 외부 사용자 대응이 필요해진 시점에서 서비스화
```

> **왜 이렇게 하는가**: 500건 데이터에 처음부터 Elasticsearch + Airflow + React를 올리는 것은 과잉 설계다. "병목이 생긴 시점에서 도구를 도입하고, 왜 도입했는지 설명할 수 있는 것"이 백엔드 엔지니어의 핵심 역량이다.

### 4.2 전체 아키텍처 (Phase 1 기준)

```
┌──────────────────────────────────────────────────────────────────┐
│                    PYTHON BATCH LAYER                             │
│                    (크롤링 + NLP)                                  │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐      │
│  │ Crawlers     │  │ NLP          │  │ Tech Blog          │      │
│  │              │  │ Pipeline     │  │ Fetcher            │      │
│  │ • Wanted API │  │              │  │                    │      │
│  │ • Jumpit     │  │ • Kiwi 형태소 │  │ • RSS Fetcher      │      │
│  │ • Greenhouse │  │ • 사전 매칭   │  │ • HTML Parser      │      │
│  │ • HTML 파싱  │  │ • TF-IDF     │  │                    │      │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘      │
│         └──────────────────┼────────────────────┘                  │
│                            │ INSERT (psycopg2 / SQLAlchemy)        │
└────────────────────────────┼─────────────────────────────────────┘
                             ▼
                  ┌──────────────────┐
                  │   PostgreSQL     │
                  │   (공유 DB)       │
                  └────────┬─────────┘
                           ▲
                           │ JPA / Spring Data
┌──────────────────────────┼──────────────────────────────────────┐
│                  SPRING BOOT API LAYER                            │
│                  (서빙 + 분석 + 스케줄링)                          │
│                                                                    │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐      │
│  │ REST API      │  │ Analysis      │  │ Scheduler        │      │
│  │               │  │ Service       │  │                  │      │
│  │ 공고 조회      │  │               │  │ Python 배치 트리거│      │
│  │ 분석 결과 조회 │  │ 빈도 집계     │  │ (ProcessBuilder  │      │
│  │ 리포트 생성    │  │ 회사 프로필    │  │  or REST call)   │      │
│  │ 스킬 사전 관리 │  │ 갭 분석       │  │                  │      │
│  └───────────────┘  └───────────────┘  └──────────────────┘      │
│                                                                    │
│  → 향후 React 대시보드 연동 (Phase 3)                              │
└──────────────────────────────────────────────────────────────────┘
```

### 4.3 왜 Java/Spring Boot + Python 이중 구조인가

| 역할 | Spring Boot (Java) | Python |
|------|--------------------|--------|
| **API 서빙** | ✅ 주력. REST API 설계, 인증, 페이지네이션 | ❌ |
| **분석 로직** | ✅ 집계 쿼리, 통계 계산, 리포트 생성 | 보조 (NLP 전처리) |
| **스케줄링** | ✅ Spring @Scheduled / Quartz | ❌ |
| **DB 접근** | ✅ Spring Data JPA, QueryDSL | INSERT only (배치) |
| **크롤링** | ❌ | ✅ requests, BeautifulSoup, Playwright |
| **NLP** | ❌ | ✅ Kiwi, scikit-learn, (선택) KeyBERT |

**면접관 예상 질문과 답변**:

> **Q**: "왜 전부 Spring Boot로 안 했나?"
> **A**: "크롤링과 NLP는 Python 생태계가 압도적입니다. requests, BeautifulSoup, Kiwi 형태소 분석기는 Java에 동등한 대안이 없습니다. 반면 API 서빙, 스케줄링, DB 접근은 제 주력인 Spring Boot로 했습니다. **도구는 문제에 맞게 선택하는 것**이고, 이 프로젝트에서는 두 언어의 강점을 분리하여 활용했습니다."

> **Q**: "Python과 Spring Boot 사이 통신은 어떻게?"
> **A**: "Phase 1에서는 Spring Boot의 `ProcessBuilder`로 Python 스크립트를 실행하고 종료 코드로 성공/실패를 판단합니다. Python이 직접 DB에 INSERT하고, Spring Boot는 DB에서 읽습니다. Phase 2에서 독립 배포가 필요해지면 Python을 경량 Flask 엔드포인트로 감싸서 HTTP 통신으로 전환합니다."

> **Q**: "Spring Boot 없이 Python으로 전부 하면 안 되나?"
> **A**: "기능적으로는 가능합니다. Python + FastAPI로 API 서빙, pandas로 분석, cron으로 스케줄링하면 됩니다. Spring Boot를 선택한 이유는 세 가지입니다: (1) 제 주력 스택이라 JPA, QueryDSL, REST API 설계 역량을 이 프로젝트에서도 보여주고 싶었고, (2) 배치와 서빙을 분리하면서 API 계약을 명확하게 설계하는 연습이 되었고, (3) 다른 프로젝트(수강신청, Kafka)와 기술 스택이 일관되어 이력서에서 Spring Boot 깊이를 보여줍니다. **솔직히 기술적 필수가 아니라 전략적 선택입니다.**"

### 4.4 기술 스택

| 영역 | 기술 | 선택 이유 |
|------|------|----------|
| **API 서버** | Spring Boot 3.x + Java 21 | 주력 백엔드 스택. 이력서의 다른 프로젝트(수강신청, Kafka)와 일관성 |
| **ORM** | Spring Data JPA + QueryDSL | 집계 쿼리에 QueryDSL 활용 |
| **크롤링** | Python + requests + BeautifulSoup | 정적 페이지. SPA는 Playwright |
| **한국어 NLP** | Kiwi (kiwipiepy) | Java 의존성 없음. 정확도 최상위. Docker 호환 |
| **키워드 추출** | 사전 매칭(핵심) + TF-IDF(보조) | 기술 용어는 대부분 고유명사 → 사전 매칭이 가장 정확 |
| **DB** | PostgreSQL | ACID. JSONB. 풀텍스트 검색. Spring Data JPA 호환 |
| **컨테이너** | Docker + Docker Compose | PostgreSQL + 앱 서버 환경 통일 |
| **빌드** | Gradle (Java) + pip/uv (Python) | 표준 도구 |
| **시각화 (MVP)** | Streamlit (Python) | 빠른 프로토타입. Phase 3에서 React 전환 |

### 4.5 기술 선택의 논리적 근거

#### 왜 PostgreSQL인가? (SQLite, MongoDB가 아닌 이유)

| 기준 | PostgreSQL | SQLite | MongoDB |
|------|-----------|--------|---------|
| Spring Data JPA 호환 | ✅ | ✅ (제한적) | ❌ (Spring Data MongoDB 별도) |
| JSONB (기술 aliases 저장) | ✅ | ❌ | ✅ |
| 풀텍스트 검색 | ✅ | ❌ | ✅ |
| 동시 쓰기 (배치+API) | ✅ | ❌ (단일 writer) | ✅ |
| 운영 복잡도 | Docker 한 줄 | 파일 하나 | Docker 한 줄 |

> **"500건에 PostgreSQL이 필요한가?"에 대한 솔직한 답변**: SQLite WAL 모드로도 이 규모에서는 충분히 동작합니다. PostgreSQL을 선택한 실제 이유는: (1) JSONB로 skill aliases를 유연하게 저장, (2) Spring Data JPA + Flyway와의 표준 통합, (3) 업계 표준 RDBMS 운영 경험 축적, (4) Docker Compose 한 줄로 띄울 수 있어 오버헤드 최소. "동시 쓰기 병목" 같은 거짓 정당화가 아니라, **이 규모에서도 합리적인 도구이고 확장 시 마이그레이션이 불필요하다**는 것이 핵심입니다.

#### 왜 Kiwi인가?

| 기준 | Kiwi (kiwipiepy) | Mecab-ko | KoNLPy |
|------|-----------------|---------|--------|
| 설치 | `pip install kiwipiepy` | C++ 빌드 필요 | Java/JVM 의존성 |
| 정확도 | 최상위 (세종 코퍼스) | 상위 | 분석기에 따라 |
| Docker 호환 | 문제 없음 | 빌드 이슈 가능 | JVM → 이미지 크기 증가 |
| 유지보수 | 활발 (v0.22.2) | 보통 | 보통 |

---

## 5. 데이터 모델

### 5.1 ERD

```
┌─────────────────────┐     ┌──────────────────────┐
│      company         │     │    job_posting        │
├─────────────────────┤     ├──────────────────────┤
│ id          (PK)     │────<│ id           (PK)     │
│ name                 │     │ company_id   (FK)     │
│ name_en              │     │ title                 │
│ category             │     │ title_normalized      │
│ (BIGTECH/BIGTECH_SUB│     │ position_type         │
│  /UNICORN/STARTUP/  │     │ (BE/PE/FDE)           │
│  SI/MID/FINANCE/    │     │ experience_level      │
│  UNCATEGORIZED)     │     │ description_raw       │
│ tags        (JSONB)  │     │ description_cleaned   │
│ aliases     (JSONB)  │     │ source_platform       │
│ careers_url          │     │ source_url            │
│ tech_blog_url        │     │ salary_min            │
│ tech_blog_type       │     │ salary_max            │
│ (rss/html/medium)    │     │ location              │
│ employee_count_range │     │ status                │
│ created_at           │     │ (ACTIVE/CLOSED/       │
│ updated_at           │     │  EXPIRED/ARCHIVED)    │
└─────────────────────┘     │ closed_at             │
                             │ posted_at             │
                             │ crawled_at            │
                             │ last_seen_at          │
                             │ created_at            │
                             └──────────┬───────────┘
                                        │
                  ┌─────────────────────┼──────────────────┐
                  ▼                     ▼                    ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│ posting_skill        │ │ skill            │ │ tech_blog_post       │
├──────────────────────┤ ├──────────────────┤ ├──────────────────────┤
│ id           (PK)    │ │ id       (PK)    │ │ id           (PK)    │
│ posting_id   (FK)    │ │ name             │ │ company_id   (FK)    │
│ skill_id     (FK)    │ │ name_ko          │ │ title                │
│ is_required          │ │ category         │ │ url                  │
│ is_preferred         │ │ aliases  (JSONB) │ │ content_raw          │
│ created_at           │ │ created_at       │ │ content_cleaned      │
└──────────────────────┘ └──────────────────┘ │ summary              │
                                               │ topics       (JSONB) │
                                               │ published_at         │
                                               │ published_year (idx) │
                                               │ crawled_at           │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────────────────┐
                                               │ blog_skill           │
                                               ├──────────────────────┤
                                               │ id           (PK)    │
                                               │ blog_post_id (FK)    │
                                               │ skill_id     (FK)    │
                                               │ mention_count        │
                                               │ created_at           │
                                               └──────────────────────┘

┌──────────────────────┐
│ unmatched_company    │    ※ 크롤링 중 company 테이블에 없는
├──────────────────────┤      회사명이 발견되면 여기에 저장.
│ id           (PK)    │      주기적으로 검토 후 company 테이블에
│ raw_name             │      카테고리와 함께 등록.
│ source_platform      │
│ posting_count        │
│ first_seen_at        │
│ resolved_company_id  │    ← 등록 완료 시 FK 연결
│ status               │
│ (PENDING/RESOLVED/   │
│  IGNORED)            │
└──────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐
│ crawl_log            │    │ analysis_snapshot     │
├──────────────────────┤    ├──────────────────────┤
│ id           (PK)    │    │ id           (PK)     │
│ source_type          │    │ snapshot_date         │
│ source_name          │    │ analysis_type         │
│ status               │    │ data         (JSONB)  │
│ items_collected      │    │ created_at            │
│ items_new            │    └──────────────────────┘
│ items_duplicate      │
│ error_message        │
│ duration_ms          │
│ started_at           │
│ finished_at          │
└──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│ trend_post           │     │ trend_skill           │
├──────────────────────┤     ├──────────────────────┤
│ id           (PK)    │────<│ id           (PK)     │
│ source               │     │ trend_post_id (FK)    │
│ (GEEKNEWS/HN/DEVTO) │     │ skill_id      (FK)    │
│ external_id          │     │ created_at            │
│ title                │     └──────────────────────┘
│ url                  │
│ score                │     ※ skill 테이블 확장:
│ comment_count        │       source_scope ENUM 추가
│ published_at         │       (JOB_POSTING / TREND / BOTH)
│ crawled_at           │       → 트렌드 전용 키워드 오염 방지
│ UNIQUE(source,       │
│   external_id)       │
└──────────────────────┘
```

### 5.2 공고 영구 보관 전략

**핵심 원칙: 채용 공고는 절대 삭제하지 않는다.**

채용 공고는 마감되면 원본 페이지가 사라진다. 한 번 수집한 데이터는 **영구 보관**하여 이후 시계열 분석, 과거 비교, 이력 추적에 활용한다.

**공고 상태 생명주기**:
```
ACTIVE → CLOSED    : 원본 페이지에서 더 이상 보이지 않을 때
ACTIVE → EXPIRED   : posted_at 기준 90일 경과 + 원본 미확인 시
CLOSED → ARCHIVED  : closed_at 기준 180일 경과 (자동)
```

**상태 감지 방법**:
```
매 크롤링 시:
  1. 기존 ACTIVE 공고의 source_url 재방문 (HEAD request)
  2. 200 OK → last_seen_at 갱신
  3. 404/Gone → status = CLOSED, closed_at = now()
  4. 연속 3회 실패 → status = EXPIRED (사이트 구조 변경일 수 있음)
```

**보관 필드**:
| 필드 | 용도 |
|------|------|
| `description_raw` | 원본 HTML/텍스트 그대로 저장. 파싱 실패 시 재처리 가능 |
| `description_cleaned` | 전처리된 텍스트. 키워드 추출에 사용 |
| `last_seen_at` | 마지막으로 원본 페이지에서 확인된 시점 |
| `closed_at` | 공고가 CLOSED/EXPIRED로 전환된 시점 |

> **왜 영구 보관인가**: (1) "6개월 전에는 K8s 요구가 40%였는데 지금은 54%다" 같은 시계열 분석은 과거 데이터 없이 불가능. (2) 특정 회사의 채용 패턴 변화를 추적할 수 있다. (3) 데이터가 쌓일수록 분석 가치가 증가하는 구조 — 이 프로젝트의 장기적 경쟁력.

> **저장 공간 우려**: 공고 1건당 description_raw + description_cleaned ≈ 5~10KB. 10,000건 = ~100MB. PostgreSQL에서 문제 없는 규모.

### 5.3 기술 용어 정규화 사전 (skill 테이블)

이 프로젝트의 **핵심 자산**. 한국어 채용 공고에서 기술 용어의 다양한 표기를 통합.

```json
{"name": "Spring Boot", "name_ko": "스프링 부트", "category": "framework",
 "aliases": ["SpringBoot", "스프링부트", "Spring-Boot", "spring boot"]}

{"name": "Kubernetes", "name_ko": "쿠버네티스", "category": "devops",
 "aliases": ["K8s", "k8s", "쿠버네티스", "쿠베", "Kube"]}

{"name": "React", "name_ko": "리액트", "category": "framework",
 "aliases": ["ReactJS", "React.js", "리액트", "react"]}
```

**카테고리 분류**:
```
language    | Java, Python, Go, Kotlin, TypeScript
framework   | Spring Boot, Django, React, Next.js
database    | MySQL, PostgreSQL, MongoDB, Redis
messaging   | Kafka, RabbitMQ, SQS
devops      | Docker, Kubernetes, Terraform, AWS
concept     | MSA, Event-Driven, DDD, TDD, CI/CD
ai_ml_model  | LLM, GPT, Claude(모델), RAG, LangChain, LlamaIndex, Vector DB, Embedding, Fine-tuning, RLHF, Transformer
ai_ml_devtool| GitHub Copilot, Cursor, Claude Code, AI coding assistant, prompt engineering, vibe coding, AI Agent, MCP
```

> **왜 ai_ml을 두 개로 나누는가**: "LLM 경험 필수"는 AI 제품을 만드는 스킬이고, "AI 도구 활용 경험 우대"는 AI로 개발하는 워크플로 스킬이다. 이 둘을 합산하면 "AI 스킬 요구 X%"라는 수치가 **무엇을 의미하는지 알 수 없다**. 분리해야 "AI 제품 스킬은 N%, AI 워크플로 스킬은 M%"라는 actionable insight가 나온다.

**ai_ml_devtool 시드 (바이브 코딩 키워드)**:
```json
{"name": "GitHub Copilot", "aliases": ["Copilot", "코파일럿", "깃허브 코파일럿"], "source_scope": "BOTH"}
{"name": "Cursor", "aliases": ["커서 IDE", "Cursor IDE"], "source_scope": "BOTH"}
{"name": "Claude Code", "aliases": ["Claude CLI", "클로드 코드"], "source_scope": "TREND"}
{"name": "prompt engineering", "aliases": ["프롬프트 엔지니어링", "프롬프트 설계"], "source_scope": "BOTH"}
{"name": "vibe coding", "aliases": ["바이브 코딩", "바이브코딩"], "source_scope": "TREND"}
{"name": "agentic workflow", "aliases": ["에이전틱 워크플로", "AI 에이전트 워크플로"], "source_scope": "TREND"}
{"name": "AI coding assistant", "aliases": ["AI 코딩 어시스턴트", "AI 코딩 도구", "AI 보조 개발"], "source_scope": "BOTH"}
{"name": "MCP", "aliases": ["Model Context Protocol", "모델 컨텍스트 프로토콜"], "source_scope": "TREND"}
{"name": "AI pair programming", "aliases": ["AI 페어 프로그래밍", "AI 짝 프로그래밍"], "source_scope": "TREND"}
{"name": "Codeium", "aliases": ["코디움"], "source_scope": "TREND"}
{"name": "Windsurf", "aliases": ["윈드서프"], "source_scope": "TREND"}
{"name": "AI-assisted development", "aliases": ["AI 활용 개발", "AI 도구 활용", "생성형 AI 활용"], "source_scope": "BOTH"}
```

> **"bare AI" 매칭 주의**: "AI"를 단독 키워드로 등록하면 "AI 면접", "SK AI" 등 대량 오탐 발생. **반드시 복합어(AI + 인접 단어) 패턴으로만 매칭**한다. 예: `"AI\s+(도구|활용|개발|코딩|보조|에이전트)"` 정규식.

**source_scope 분류** (트렌드 키워드 오염 방지):
```
JOB_POSTING  | 채용 공고에서만 등장하는 키워드 (예: "경력 3년 이상")
TREND        | 트렌드 뉴스에서만 등장하는 키워드 (예: "vibe coding", "MCP")
BOTH         | 양쪽 모두에서 등장 (예: "Kubernetes", "GitHub Copilot") — Buzz vs Hiring 비교 대상
```

> 트렌드 전용 키워드(TREND)는 채용 분석에서 제외되고, 채용 전용 키워드(JOB_POSTING)는 트렌드 분석에서 제외된다. **Buzz vs Hiring 비교는 BOTH만 대상**이다. TREND-only 키워드(vibe coding, MCP 등)는 별도 "AI 트렌드 리포트"에서 "채용 미반영 트렌드"로 제공한다.

**사전 구축 전략**:
1. **수동 시드 (100개)**: 채용 공고에서 자주 등장하는 기술 100개를 aliases 포함하여 등록
2. **미매칭 키워드 리포트**: 사전에 없는 키워드를 별도 테이블에 수집 → 주기적으로 사전에 추가
3. 선정 기준: [awesome-devblog](https://github.com/awesome-devblog/awesome-devblog) + 실제 크롤링 데이터의 빈출 키워드 기반

---

## 6. 핵심 기능 설계

### 6.1 Feature 1: 크롤러 (Python 배치)

**크롤러 인터페이스**:
```python
class BaseCrawler(ABC):
    @abstractmethod
    def crawl(self) -> list[RawJobPosting]: ...
    def get_source_name(self) -> str: ...
```

**구현체 (우선순위 순)**:
1. `WantedAPICrawler` — 원티드 OpenAPI (가장 안정적, 1순위)
2. `JumpitCrawler` — 점핏 공개 페이지 XHR 파싱
3. `GreenhouseCrawler` — 쿠팡, 두나무 (Board API)
4. `TechBlogFetcher` — RSS + HTML 파싱

**크롤링 규칙**:
- Rate Limit: **도메인당 1 req/sec** (robots.txt crawl-delay 준수)
- 재시도: 429/503 → Exponential Backoff (1s, 2s, 4s, 최대 3회)
- User-Agent: `DevPulse-Bot/1.0 (+contact@email.com)`
- 동시성: `asyncio.Semaphore(3)` — 최대 3개 도메인 동시 크롤링
- 중복 제거: `(company_name_normalized, title_normalized, posted_date)` 기준

**회사명 정규화 문제 대응**:
"우아한형제들" vs "배달의민족" vs "배민" → `company` 테이블의 `name`, `name_en` + aliases로 매핑

**수집 주기**:
- 채용 플랫폼: **주 2회** (월/목 새벽, Spring @Scheduled로 Python 배치 트리거)
- 테크 블로그: **주 1회** (일요일)

### 6.2 Feature 2: 키워드 추출 (Python 배치)

**핵심 원칙: 사전 매칭이 주력이고, NLP는 보조다.**

채용 공고의 기술 키워드는 대부분 **영어 고유명사** (Java, Spring Boot, Kafka, Docker, AWS...)이다. 한국어 형태소 분석보다 **사전 매칭이 훨씬 정확하다**. NLP는 사전에 없는 키워드를 발굴하는 보조 역할이다.

**추출 프로세스**:

```
Input: 채용 공고 텍스트
  │
  ▼
[Step 1] 기술 용어 사전 매칭 (Dictionary Match) — 핵심
  • skill 테이블의 name + aliases와 정규표현식 매칭
  • 대소문자 무시, 경계 문자 확인 (단어 경계 \b 또는 한글 문맥)
  • "스프링부트" → "Spring Boot", "K8s" → "Kubernetes"
  • 복합 키워드 우선 매칭: "Spring Boot"를 먼저 매칭, 그 다음 "Spring"
  • **정확도: 사전에 있으면 ~100%**
  │
  ▼
Output: [{skill_id: 1, skill_name: "Spring Boot", is_required: true, method: "dict_match"}, ...]

[Phase 2에서 추가] Kiwi 형태소 분석 → 미매칭 키워드 후보 추출
  • Phase 1에서 사전 매칭의 recall이 목표(0.75) 미달일 때 도입
  • Step 1에서 매칭되지 않은 텍스트에서 명사(NNG, NNP), 외래어(SL) 추출
  • 미매칭 후보를 별도 테이블에 저장 → 검토 후 사전 추가
  • **도입 조건**: "사전 커버리지가 부족하다"는 데이터 근거가 있을 때만

[Phase 3에서 추가] TF-IDF 빈도 보정 (데이터 1,000건 이상일 때)
  • 전체 코퍼스 대비 특정 회사/포지션에서 특이하게 많이 등장하는 키워드 탐지
  • 500건 미만에서는 IDF 값이 통계적으로 불안정
```

> **"5-Layer Pipeline이라고 안 하는 이유"**: 라이브러리 호출을 순서대로 한 것을 "N-Layer Pipeline"이라고 부르는 것은 과장이다. 실제로는 **사전 매칭 1개 + 보조 NLP 2개**다. 면접에서 솔직하게 "핵심은 사전 매칭이고, Kiwi와 TF-IDF는 사전 커버리지를 넓히는 보조"라고 설명한다.

### 6.3 Feature 3: 분석 엔진 (Spring Boot)

#### 3-1. 기술 스냅샷 분석 (MVP 핵심)

| 분석 항목 | 설명 | SQL 기반 |
|----------|------|----------|
| **기술 키워드 빈도 Top N** | 전체 공고에서 가장 많이 요구되는 기술 | `GROUP BY skill_id ORDER BY COUNT(*) DESC` |
| **포지션별 기술 비교** | BE vs PE vs FDE 기술 요구 차이 | `GROUP BY position_type, skill_id` |
| **회사별 기술 프로필** | 네이버/쿠팡/토스 등 회사별 기술 스택 | `GROUP BY company_id, skill_id` |
| **필수 vs 우대 분리** | "필수 자격"에 있는 기술 vs "우대 사항"의 기술 | `is_required` 필드 기반 |
| **기술 동시 요구 패턴** | "Kafka를 요구하는 곳은 동시에 뭘 요구하는가?" | self-join on posting_id |

> **시계열 분석은 MVP에서 제외한다.** 월별 트렌드를 보려면 최소 6개월 데이터가 필요하다. 500건 초기 수집으로 "↑5%"를 말하는 것은 통계적으로 무의미하다. 데이터가 6개월 이상 축적된 Phase 3에서 도입하되, 그때 "데이터가 충분해진 시점에서 시계열을 추가했다"는 것이 오히려 **판단력**을 보여준다.

#### 3-2. 블로그 참조 분석

테크 블로그 키워드와 채용 공고 키워드를 비교하되, **통계적 한계를 인정**한다.

| 카테고리 | 정의 | 해석 | 한계 |
|----------|------|------|------|
| 공고 ∩ 블로그 | 양쪽 모두에서 언급 | **핵심 기술일 가능성 높음** | 블로그 커버리지가 낮으면 신뢰도 하락 |
| 공고만 | 공고에는 있고 블로그에는 없음 | 해석 불가 (블로그를 안 쓴 것일 수 있음) | **부재의 증거 ≠ 증거의 부재** |
| 블로그만 | 블로그에만 있고 공고에는 없음 | 내부에서 쓰지만 신입에게는 안 요구하는 기술일 수 있음 | 블로그 주제 편향 존재 |

> **선제적 한계 인정**: "회사당 블로그 글이 평균 20~30건일 때, 이 분석은 참고 지표일 뿐 결론이 아닙니다. 블로그를 쓰는 팀은 전체의 일부이고, NDA 때문에 못 쓰는 핵심 기술이 많습니다." — 면접에서 이 한계를 먼저 말하면 **분석적 사고**를 보여줄 수 있다.

#### 3-3. 갭 분석

**이전 설계의 문제점**: "내 숙련도 4점"과 "시장 빈도 89%"는 단위가 달라서 뺄셈이 무의미했다.

**수정된 갭 분석**:

```
[Step 1] 이진 분류: 시장이 요구하는 기술 중 내가 보유/미보유 판별
  ┌──────────────────────┬──────────┬───────────┐
  │ 기술 (시장 빈도순)    │ 시장 빈도 │ 보유 여부  │
  ├──────────────────────┼──────────┼───────────┤
  │ Java                 │ 89%      │ ✅ 보유    │
  │ Spring Boot          │ 82%      │ ✅ 보유    │
  │ AWS                  │ 67%      │ ⚠️ 기초    │
  │ Docker               │ 61%      │ ✅ 보유    │
  │ Kubernetes           │ 54%      │ ❌ 미보유  │  ← 학습 우선순위 1
  │ Kafka                │ 48%      │ ⚠️ 학습중  │
  │ Redis                │ 45%      │ ⚠️ 기초    │
  │ MSA                  │ 42%      │ ❌ 미보유  │  ← 학습 우선순위 2
  └──────────────────────┴──────────┴───────────┘

[Step 2] 학습 우선순위 = 미보유 기술 중 시장 빈도가 높은 순
  1. Kubernetes (54%) — 미보유 중 가장 높은 빈도
  2. MSA (42%)
  3. CI/CD (38%)
```

> 내 스킬셋은 수동 입력 (3단계: 보유/기초/미보유). 주관적 레벨 점수를 빈도 퍼센트와 혼합하지 않는다.

### 6.4 Feature 4: 리포트 생성 (Spring Boot)

**스냅샷 리포트** (시계열이 아님):

> **⚠️ 아래 리포트는 설계 검증용 가상 데이터입니다. 실제 수치는 Phase 1 완료 후 대체됩니다.**

```markdown
# DevPulse 분석 리포트 (2026-03-10 스냅샷)

## 데이터 현황
- 분석 대상 공고: 523건 (원티드 312건, 점핏 148건, 직접 수집 63건)
- 분석 대상 블로그: 287건 (15개 블로그)
- 타겟 회사: 17개 (Big 7 + 유니콘 10)

## Backend Engineer 기술 키워드 Top 15
1. Java (89%) — 거의 모든 공고에서 요구
2. Spring Boot (82%)
3. AWS (67%)
...

## 포지션별 차이
- BE는 Java/Spring 중심, PE는 TypeScript/React 비중 높음
- FDE 공고가 4건뿐이라 통계적 유의성 없음 (참고만)

## 회사별 특이점
- 토스: Kotlin 비중이 다른 회사 대비 2배 (32% vs 평균 15%)
- 쿠팡: AWS 요구 100%, 다른 클라우드 언급 0건

## 블로그 참조 (참고 지표, 한계 있음)
- 배민 블로그: "이벤트 소싱", "CQRS" 빈출 → 공고에서는 "MSA" 수준으로 요구
- 토스 블로그: "Kotlin Coroutines" 집중 → 공고에서 Kotlin 직접 요구

## Buzz vs Hiring Gap (GeekNews 30일 vs 채용 공고)
| 기술 | 뉴스 언급 | 뉴스 순위 | 공고 빈도 | 공고 순위 | 분류 |
|------|----------|----------|----------|----------|------|
| LangChain | 47회 | 2위 | 3.1% | 34위 | ⚡ OVERHYPED |
| Rust | 38회 | 3위 | 1.5% | 41위 | ⚡ OVERHYPED |
| Kafka | 12회 | 8위 | 48.0% | 5위 | ✅ ADOPTED |
| Java | 5회 | 22위 | 88.9% | 1위 | 🏛️ ESTABLISHED |

→ LangChain, Rust는 커뮤니티 관심 대비 채용 수요 낮음 — 학습 우선순위 하향
→ Kafka는 관심과 수요 모두 높음 — 학습 가치 확실
→ Java는 더 이상 화제가 아니지만 시장의 기본기 — 반드시 보유해야

## AI 트렌드 (두 축으로 분리)

### AI-as-Product (ai_ml_model) — "AI 제품을 만드는 스킬"
- LLM (뉴스 1위, 공고 2.1%) — 논의 활발, 채용 요건은 ML 포지션에 집중
- RAG (뉴스 4위, 공고 0.8%) — 실무 적용 초기
- Fine-tuning (뉴스 7위, 공고 0.4%) — 극소수 ML팀에서만 요구

### AI-as-Workflow (ai_ml_devtool) — "AI로 개발하는 스킬"
- GitHub Copilot (뉴스 6위, 공고 1.2%) — 유일하게 공고에 등장하기 시작
- prompt engineering (뉴스 3위, 공고 0.6%) — 공고에 간헐적 등장
- vibe coding (뉴스 5위, 공고 0건) — 순수 트렌드. 채용 미반영
- MCP (뉴스 8위, 공고 0건) — 순수 트렌드. 채용 미반영

→ **핵심 인사이트**: AI-as-Workflow 스킬은 아직 한국 채용 시장에 공식 반영되지 않았다.
  하지만 GeekNews에서 AI 관련 논의가 전체의 X%를 차지하며, 이 Gap은 좁혀질 것이다.
  **지금 역량을 갖추면 시장이 따라올 때 선점 우위가 된다.**

## 나의 갭
- 미보유 중 시장 빈도 상위: Kubernetes (54%), MSA (42%)
- 권장: Kubernetes 학습을 최우선으로
```

### 6.5 Feature 5: Buzz vs Hiring Gap 분석 (Phase 2)

**핵심 가치**: "업계가 떠드는 것"과 "실제로 채용하는 것"의 Gap을 정량화한다.

> **왜 이게 중요한가**: GeekNews에서 "LangChain"이 매주 등장해도, 한국 백엔드 공고에서 LangChain을 요구하는 곳은 3%일 수 있다. 반면 "Kafka"는 뉴스에 덜 나오지만 공고의 48%가 요구한다. **이 Gap을 모르면 유행에 끌려 비효율적으로 공부한다.**

#### 5-1. 트렌드 데이터 수집 (Python 배치)

```python
class TrendCrawler(ABC):
    @abstractmethod
    def crawl(self) -> list[TrendPost]: ...

class GeekNewsCrawler(TrendCrawler):
    """GeekNews RSS 피드 수집 (news.hada.io/rss/news)"""
    # RSS → title, url, score(없으면 0), published_at
    # 기존 skill 사전으로 title에서 키워드 매칭

class HackerNewsCrawler(TrendCrawler):  # Phase 2
    """HN Firebase API (hacker-news.firebaseio.com/v0/)"""
    # /topstories, /beststories → item detail → title, score, descendants
```

**수집 주기**: 매일 1회 (트렌드 뉴스는 채용 공고보다 속도가 빠름)
**보존 기간**: 90일 rolling window (트렌드는 시간에 민감)

#### 5-2. Buzz vs Hiring 분류 (2×2 매트릭스)

```
                    채용 공고 빈도
                    High              Low
              ┌─────────────────┬─────────────────┐
   트렌드     │                 │                 │
   언급 빈도  │   ✅ ADOPTED     │  ⚡ OVERHYPED   │
   High       │  (채택됨)        │  (과대 포장)     │
              │  Kafka, K8s     │  LangChain?     │
              ├─────────────────┼─────────────────┤
              │                 │                 │
   Low        │  🏛️ ESTABLISHED │  🌱 EMERGING    │
              │  (정착됨)        │  (태동기)        │
              │  Java, MySQL    │  새 프레임워크?   │
              └─────────────────┴─────────────────┘
```

**분류 기준** (빈도 기반, 순위 비교가 아님):
- **trend_frequency**: 최근 30일간 GeekNews 전체 포스트 중 해당 키워드 언급 비율 (%)
- **job_frequency**: 전체 채용 공고 중 해당 키워드 등장 비율 (%)
- **High/Low 경계**: trend_frequency >= 5% = High, job_frequency >= 10% = High
  - 이 임계값은 Phase 1 실제 데이터 분포를 보고 조정한다 (데이터 기반 캘리브레이션)
- **분류**: `OVERHYPED` / `ADOPTED` / `ESTABLISHED` / `EMERGING`

> **왜 순위(rank) 비교가 아닌 빈도(%) 비교인가**: 트렌드와 채용은 모집단 크기가 다르다 (247 포스트 vs 523 공고). 순위 25%를 비교하면 12위와 13위의 차이에 분류가 뒤집히는 불안정한 결과가 나온다. 빈도 %는 각 모집단 내에서의 절대적 비중을 나타내므로 더 안정적이다. 단, **소표본(30건 미만) 구간에서는 분류를 생략하고 절대 건수만 표시**한다.

**분석 로직 (Spring Boot)**:
```java
// BuzzHiringGapService.java
public List<BuzzHiringGap> analyze(int topN, int trendDays) {
    // 1. trend_skill에서 최근 N일간 skill별 언급 횟수 집계
    // 2. posting_skill에서 skill별 공고 등장 횟수 집계
    // 3. 각각 rank 매기기 (1 = 가장 많이 언급/요구)
    // 4. source_scope = BOTH인 skill만 비교 대상
    // 5. 2x2 매트릭스 분류
}
```

#### 5-3. AI 트렌드 별도 트래킹 (ai_ml_model + ai_ml_devtool)

AI 분석은 **두 축**으로 분리한다:

| 축 | 카테고리 | 의미 | 예시 |
|----|---------|------|------|
| **AI-as-Product** | `ai_ml_model` | AI 제품을 만드는 스킬 | LLM, RAG, Fine-tuning, LangChain |
| **AI-as-Workflow** | `ai_ml_devtool` | AI로 개발하는 워크플로 스킬 | Copilot, Cursor, vibe coding, prompt engineering |

```
분석 1: AI 스킬 채용 현황 (스냅샷)
  "전체 백엔드 공고 중 AI 관련 키워드 포함 비율"
  → ai_ml_model: N% (LLM/RAG 등 AI 제품 스킬)
  → ai_ml_devtool: M% (Copilot/AI 도구 활용 등 워크플로 스킬)
  → ⚠️ 10건 미만이면 비율 대신 절대 건수만 표시

분석 2: AI Buzz vs Hiring Gap
  → source_scope=BOTH인 AI 키워드만 2×2 분류
  → source_scope=TREND인 AI 키워드는 "채용 미반영 트렌드" 리포트

분석 3: 회사별 AI 얼리 어답터 (Phase 2)
  → "어떤 회사가 AI 도구를 공고에 먼저 반영하는가?"
  → company별 AI 키워드 포함 공고 비율 순위
```

> **예상 결과와 해석**: AI 키워드 대부분은 TREND scope일 것이다 (채용 미반영). 이것은 **실패가 아니라 발견**이다. "한국 백엔드 시장에서 AI 워크플로 스킬은 아직 공식 요구사항이 아니다. 하지만 GeekNews에서 AI 관련 논의가 전체의 X%를 차지한다. 이 Gap은 1~2년 내 좁혀질 가능성이 높고, 그 전에 역량을 갖추는 것이 전략적 우위다." — 이 서사가 면접에서의 핵심 메시지.

> **all-OVERHYPED 시나리오 대비**: AI 키워드가 전부 OVERHYPED로 분류되면 분석에 차별성이 없다. 이 경우 2×2 분류 대신 **"채용 진입 시점 추적"**으로 전환한다: "이번 달 처음으로 Copilot이 공고 2건에 등장했다" → 시계열 데이터 축적 후(Phase 3) "AI 워크플로 스킬 최초 등장 시점" 분석이 가능해진다.

#### 5-4. 이 기능의 한계 (선제적 명시)

| 한계 | 설명 |
|------|------|
| GeekNews는 1인 큐레이션 | xguru 1인이 선별. 개인 편향 존재. HN 추가로 완화 가능 |
| 커뮤니티 관심 ≠ 산업 채택 | "재미있는 기술"과 "돈이 되는 기술"은 다를 수 있음 |
| 한국 시장 특수성 | 글로벌 트렌드가 한국 채용에 반영되기까지 시차 존재 |
| 30일 window 한계 | 컨퍼런스(KubeCon 등) 시기에 일시적 스파이크 발생 → 4주 이동평균으로 완화 |

> **면접 답변**: "이 분석은 '참고 지표'입니다. GeekNews는 한국 개발자 커뮤니티의 관심을 대략적으로 반영하지만, 1인 큐레이션의 편향이 있고, 커뮤니티 관심과 실제 채용은 다릅니다. 그래서 'OVERHYPED'라고 분류된 기술을 안 배우는 게 아니라, **학습 우선순위를 정할 때 채용 빈도에 더 높은 가중치를 둔다**는 뜻입니다."

#### 5-5. 검증 (Phase 0에서 수행)

이 기능을 구현하기 전, **수동으로 검증**한다:
1. GeekNews 최근 30일 글 제목에서 기술 키워드 수동 추출 (20개)
2. Phase 0에서 수집한 채용 공고 50건의 키워드 Top 20과 비교
3. **Gap이 흥미로운가?** (예: "LangChain은 뉴스 3위인데 공고에는 없다")
4. Gap이 trivial하면 (대부분 키워드가 양쪽 비슷하면) → 이 기능 축소 또는 제외

### 6.6 Feature 6: 블로그 주제 요약 + 연도별 트렌드 (Phase 2)

**핵심 가치**: 주요 회사들이 **어떤 기술적 도전을 해결해왔는지** 연도별로 보여준다.

> "배민은 2019~2020년에 MSA 전환을 집중적으로 다뤘고, 2022년부터 이벤트 소싱/CQRS로 주제가 이동했다. 토스는 2021년부터 Kotlin Coroutines를 집중 논의하기 시작했다." — 이런 인사이트는 개별 블로그를 읽어서는 **전체 흐름**을 파악하기 어렵다.

#### 6-1. 블로그 글 요약 (Python 배치)

각 블로그 글에서 **1~2문장 요약 + 주제 태그**를 추출한다.

**요약 방법 (비용 순)**:

| 방법 | 비용 | 정확도 | Phase |
|------|------|--------|-------|
| **추출적 요약 (MVP)** | 무료 | 중 | Phase 2 |
| LLM API 요약 | ~$0.01/글 | 상 | Phase 3 |

```python
# Phase 2: 추출적 요약 (비용 0)
def summarize_extractive(content: str) -> str:
    """첫 문단 + 제목에서 핵심 1~2문장 추출"""
    # 1. 제목 자체가 핵심 요약 (대부분의 기술 블로그)
    # 2. 첫 문단에서 "이 글에서는...", "소개합니다" 패턴 탐지
    # 3. fallback: 첫 2문장

# Phase 3: LLM 요약 (정확도 향상)
def summarize_llm(content: str) -> str:
    """Claude/GPT API로 1~2문장 요약 + 주제 태그 추출"""
    # prompt: "이 기술 블로그 글을 1~2문장으로 요약하고,
    #          주제 태그를 3~5개 추출하세요."
    # 비용: ~2,000글 × $0.01 = ~$20 (1회성)
```

#### 6-2. 주제(Topic) 추출

블로그 글의 주제를 **2단계**로 태깅한다.

```
[Level 1] 기술 키워드 (기존 skill 사전 매칭)
  → "Kafka", "Kubernetes", "Spring Boot" 등 구체적 기술명

[Level 2] 주제 카테고리 (별도 topic_category 사전)
  → 기술 키워드보다 넓은 개념. 면접에서 "이 회사는 어떤 문제를 풀고 있는가?" 파악용
```

**topic_category 시드 (수동 관리, 30개)**:
```
architecture   | MSA 전환, 모놀리스, DDD, 헥사고날 아키텍처
data           | 데이터 파이프라인, ETL, 실시간 처리, 데이터 레이크
performance    | 성능 최적화, 캐싱, 쿼리 튜닝, 부하 테스트
infra          | Kubernetes 도입, CI/CD, IaC, 모니터링, 장애 대응
language       | Kotlin 전환, Java 버전 업그레이드, TypeScript 도입
testing        | TDD, 테스트 자동화, E2E 테스트, 카오스 엔지니어링
culture        | 코드 리뷰, 개발 문화, 온보딩, 기술 조직 운영
ai             | ML 파이프라인, 추천 시스템, LLM 활용, AI 도입
search         | 검색 엔진, Elasticsearch, 자연어 처리
payment        | 결제 시스템, 정산, PG 연동
```

**매칭 방식**: title + content_cleaned에서 topic_category 키워드 패턴 매칭.
블로그 글 제목이 "배달의민족 마이크로서비스 여행기"이면 → `topics: ["MSA 전환", "architecture"]`

#### 6-3. 연도별 주제 트렌드 분석 (Spring Boot)

```sql
-- 회사별 연도별 주제 트렌드
SELECT
  c.name AS company,
  bp.published_year,
  unnest(bp.topics) AS topic,
  COUNT(*) AS post_count
FROM tech_blog_post bp
JOIN company c ON bp.company_id = c.id
GROUP BY c.name, bp.published_year, topic
ORDER BY c.name, bp.published_year, post_count DESC;
```

**분석 항목**:

| 분석 | 설명 | 인사이트 예시 |
|------|------|-------------|
| **회사별 연도별 주요 주제** | 각 회사가 매년 어떤 주제를 가장 많이 다뤘는가 | "배민 2020: MSA 전환(12건), 2023: 이벤트 소싱(8건)" |
| **주제별 회사 분포** | 특정 주제를 어떤 회사들이 다루는가 | "Kotlin: 토스(15건), 카카오(8건), 당근(6건)" |
| **연도별 주제 부상/하락** | 전체 블로그에서 연도별로 어떤 주제가 뜨고 지는가 | "2021: K8s 급증, 2024: AI/LLM 급증, MSA는 2022 피크 후 하락" |
| **블로그→채용 선행 지표** | 블로그 주제가 채용 요구에 1~2년 선행하는지 검증 | "2021년 토스 블로그에 Kotlin 집중 → 2023년 공고에 Kotlin 필수 등장" |

> **"블로그→채용 선행 지표"의 한계**: 인과가 아니라 상관이다. "블로그에 썼으니까 나중에 채용에 반영됐다"가 아니라, 둘 다 같은 기술 트렌드의 결과일 수 있다. 면접에서는 "상관 패턴을 발견했고, 인과는 주장하지 않습니다"라고 말한다.

#### 6-4. 블로그 트렌드 리포트 예시

> **⚠️ 설계 검증용 가상 데이터입니다.**

```markdown
## 배민 (우아한형제들) 블로그 연도별 주제 트렌드
| 연도 | 1위 주제 | 2위 주제 | 3위 주제 | 총 글 수 |
|------|---------|---------|---------|---------|
| 2018 | 성능 최적화 (8건) | Java (6건) | 개발 문화 (5건) | 32건 |
| 2019 | MSA 전환 (12건) | Spring Boot (7건) | 데이터 (5건) | 41건 |
| 2020 | MSA 전환 (15건) | Kubernetes (9건) | 이벤트 드리븐 (6건) | 48건 |
| 2021 | Kubernetes (11건) | CI/CD (8건) | Kotlin (5건) | 39건 |
| 2022 | 이벤트 소싱 (9건) | Kotlin (8건) | 테스트 (6건) | 35건 |
| 2023 | Kotlin (10건) | AI/ML (7건) | 결제 시스템 (5건) | 33건 |

→ 배민의 기술 여정: Java 모놀리스 → MSA 전환(2019~2020 피크) → K8s 인프라(2021) → Kotlin + 이벤트 드리븐(2022~)
→ 2023년부터 AI/ML 주제 부상 — 향후 AI 관련 채용 요구 증가 가능성

## 전체 블로그 — 연도별 핵심 주제 변화
| 연도 | 급상승 주제 | 하락 주제 |
|------|-----------|----------|
| 2020 | MSA, Kubernetes | 모놀리스, SVN |
| 2021 | Kotlin, CI/CD | Java 8 |
| 2022 | 이벤트 소싱, Kafka | MSA (이미 정착) |
| 2023 | AI/LLM, Kotlin Coroutines | - |
| 2024 | AI Agent, RAG, 플랫폼 엔지니어링 | - |
```

### 6.7 Feature 7: 대시보드 (Phase 3)

**MVP**: Streamlit으로 빠르게 프로토타입. Spring Boot API에서 데이터를 가져와 시각화.
**Phase 3**: React + Recharts 기반 대시보드로 전환.

---

## 7. API 설계 (Spring Boot)

### 7.1 공고 조회

```
GET  /api/v1/postings
     ?positionType=BACKEND
     &companyCategory=BIGTECH,BIGTECH_SUB,UNICORN  # 복수 선택 가능 (콤마 구분)
     &skillName=java,spring-boot
     &status=ACTIVE,CLOSED                          # 마감된 공고도 조회 가능
     &dateFrom=2026-01-01&dateTo=2026-03-04
     &page=0&size=20&sort=postedAt,desc

GET  /api/v1/postings/{id}

# 카테고리 필터 옵션:
# BIGTECH      — 네이버, 쿠팡, 카카오, 라인, 배민, 토스, 당근
# BIGTECH_SUB  — 카카오페이, 카카오뱅크, 네이버클라우드 등
# UNICORN      — 야놀자, 직방, 리디, 뱅크샐러드, 컬리, 무신사, 두나무 등
# STARTUP      — 센드버드, 채널톡, 토스랩 등
# SI           — 삼성SDS, LG CNS 등
# MID          — NHN, 카페24 등
# FINANCE      — 카카오뱅크, 토스 등 (태그 기반 보조 필터)
# UNCATEGORIZED — 아직 미분류된 회사
```

### 7.2 분석 결과 조회

```
GET  /api/v1/analysis/skill-ranking
     ?positionType=BACKEND
     &companyCategory=BIGTECH,UNICORN              # 복수 선택 가능
     &includeClosedPostings=true                    # 마감 공고 포함 여부 (기본: false)
     &topN=20

GET  /api/v1/analysis/company-profile/{companyId}

GET  /api/v1/analysis/position-comparison
     ?positions=BACKEND,PRODUCT

GET  /api/v1/analysis/co-occurrence
     ?skillName=kafka&topN=10

POST /api/v1/analysis/gap
     {"mySkills": [{"name": "Java", "status": "OWNED"}, {"name": "K8s", "status": "NOT_OWNED"}]}

GET  /api/v1/analysis/blog-reference/{companyId}

GET  /api/v1/analysis/blog-topics/company/{companyId}
     ?fromYear=2018&toYear=2026                    # 회사별 연도별 주제 트렌드

GET  /api/v1/analysis/blog-topics/yearly-trend
     ?topN=5&fromYear=2018&toYear=2026             # 전체 블로그 연도별 주제 부상/하락

GET  /api/v1/analysis/blog-topics/topic/{topicName}
     ?fromYear=2018&toYear=2026                    # 특정 주제를 다루는 회사 분포

GET  /api/v1/analysis/blog-to-hiring-lag
     ?companyId=1&skillName=kotlin                 # 블로그→채용 선행 지표 (상관 분석)
```

### 7.3 트렌드 분석

```
GET  /api/v1/analysis/trend-ranking
     ?source=GEEKNEWS&period=LAST_30_DAYS&topN=20

GET  /api/v1/analysis/buzz-vs-hiring
     ?topN=20&period=LAST_30_DAYS

GET  /api/v1/analysis/buzz-vs-hiring/ai
     ?topN=10&period=LAST_30_DAYS
```

#### 응답 예시

```json
// GET /api/v1/analysis/buzz-vs-hiring?topN=5
{
  "snapshotDate": "2026-03-10",
  "trendPeriod": "LAST_30_DAYS",
  "trendSource": "GEEKNEWS",
  "totalTrendPosts": 247,
  "totalJobPostings": 523,
  "gaps": [
    {
      "skill": "Kafka",
      "trendMentions": 12, "trendRank": 8,
      "jobPostings": 251, "jobRank": 5, "jobPercentage": 48.0,
      "classification": "ADOPTED",
      "insight": "커뮤니티 관심과 채용 수요 모두 높음"
    },
    {
      "skill": "LangChain",
      "trendMentions": 47, "trendRank": 2,
      "jobPostings": 16, "jobRank": 34, "jobPercentage": 3.1,
      "classification": "OVERHYPED",
      "insight": "커뮤니티 관심 대비 채용 수요 낮음 — 학습 우선순위 하향 권장"
    },
    {
      "skill": "Java",
      "trendMentions": 5, "trendRank": 22,
      "jobPostings": 465, "jobRank": 1, "jobPercentage": 88.9,
      "classification": "ESTABLISHED",
      "insight": "더 이상 화제가 아니지만 채용 시장의 기본기"
    },
    {
      "skill": "Rust",
      "trendMentions": 38, "trendRank": 3,
      "jobPostings": 8, "jobRank": 41, "jobPercentage": 1.5,
      "classification": "OVERHYPED",
      "insight": "글로벌 관심 높으나 한국 백엔드 채용에서는 극소수"
    },
    {
      "skill": "Docker",
      "trendMentions": 8, "trendRank": 14,
      "jobPostings": 319, "jobRank": 4, "jobPercentage": 61.0,
      "classification": "ESTABLISHED",
      "insight": "뉴스에서는 당연시되지만 채용에서는 여전히 핵심 요구"
    }
    // ※ MCP, vibe coding 등 source_scope=TREND 키워드는
    //   이 API에서 제외됨. 별도 /buzz-vs-hiring/ai 엔드포인트에서 제공.
  ]
}
```

### 7.4 관리

```
GET  /api/v1/admin/skills
POST /api/v1/admin/skills
PATCH /api/v1/admin/skills/{id}

GET  /api/v1/admin/crawl-logs?source=wanted&status=SUCCESS&page=0&size=20

POST /api/v1/admin/crawl/trigger   # Python 배치 수동 트리거

GET  /api/v1/admin/health
```

### 7.4 응답 예시

> **⚠️ 아래 모든 수치는 설계 검증용 가상 데이터이며, 실제 수집 후 대체됩니다.** 면접에서 이 숫자를 실측값으로 제시하면 안 됩니다.

```json
// GET /api/v1/analysis/skill-ranking?positionType=BACKEND&topN=5
{
  "snapshotDate": "2026-03-10",
  "totalPostings": 523,
  "positionType": "BACKEND",
  "rankings": [
    {"rank": 1, "skill": "Java", "count": 465, "percentage": 88.9, "requiredRatio": 0.76},
    {"rank": 2, "skill": "Spring Boot", "count": 429, "percentage": 82.0, "requiredRatio": 0.71},
    {"rank": 3, "skill": "AWS", "count": 351, "percentage": 67.1, "requiredRatio": 0.45},
    {"rank": 4, "skill": "Docker", "count": 319, "percentage": 61.0, "requiredRatio": 0.38},
    {"rank": 5, "skill": "Kubernetes", "count": 283, "percentage": 54.1, "requiredRatio": 0.22}
  ]
}
```

---

## 8. 프로젝트 구조

```
devpulse/
├── docker-compose.yml                # PostgreSQL
├── README.md
├── CLAUDE.md                          # AI 에이전트 지침
│
├── api/                               # Spring Boot API
│   ├── build.gradle
│   ├── Dockerfile
│   └── src/
│       ├── main/java/com/devpulse/
│       │   ├── DevPulseApplication.java
│       │   ├── config/
│       │   │   └── SchedulerConfig.java
│       │   ├── domain/
│       │   │   ├── company/           # Company entity, repository, service
│       │   │   ├── posting/           # JobPosting entity, repository, service
│       │   │   ├── skill/             # Skill entity, repository, service
│       │   │   ├── blog/              # TechBlogPost entity, repository
│       │   │   ├── trend/             # TrendPost, TrendSkill entity, repository
│       │   │   └── analysis/          # AnalysisSnapshot entity
│       │   ├── api/
│       │   │   ├── PostingController.java
│       │   │   ├── AnalysisController.java
│       │   │   ├── TrendController.java        # 트렌드 분석 API
│       │   │   ├── AdminController.java
│       │   │   └── dto/               # Request/Response DTOs
│       │   ├── service/
│       │   │   ├── SkillRankingService.java
│       │   │   ├── CompanyProfileService.java
│       │   │   ├── GapAnalysisService.java
│       │   │   ├── BuzzHiringGapService.java   # Buzz vs Hiring 비교
│       │   │   ├── BlogTopicTrendService.java # 블로그 연도별 주제 트렌드
│       │   │   ├── ReportService.java
│       │   │   └── CrawlTriggerService.java    # Python 배치 트리거
│       │   └── scheduler/
│       │       └── CrawlScheduler.java          # @Scheduled 배치 실행
│       ├── main/resources/
│       │   ├── application.yml
│       │   └── db/migration/                    # Flyway 마이그레이션
│       └── test/java/com/devpulse/
│           ├── service/
│           │   ├── SkillRankingServiceTest.java
│           │   └── GapAnalysisServiceTest.java
│           ├── api/
│           │   ├── PostingControllerTest.java
│           │   └── AnalysisControllerTest.java
│           └── integration/
│               └── CrawlIntegrationTest.java
│
├── batch/                              # Python 배치 (크롤링 + NLP)
│   ├── requirements.txt
│   ├── crawlers/
│   │   ├── base.py
│   │   ├── wanted.py
│   │   ├── jumpit.py
│   │   ├── greenhouse.py
│   │   ├── tech_blog.py
│   │   └── trend/
│   │       ├── base.py               # TrendCrawler ABC
│   │       ├── geeknews.py           # GeekNews RSS 수집
│   │       └── hackernews.py         # HN Firebase API (Phase 2)
│   ├── nlp/
│   │   ├── skill_matcher.py            # 사전 기반 매칭 (핵심)
│   │   ├── tokenizer.py                # Kiwi 형태소 분석 (보조)
│   │   ├── normalizer.py               # 직무명/회사명 정규화
│   │   ├── topic_extractor.py         # 블로그 주제 태깅
│   │   └── summarizer.py             # 추출적 요약 (Phase 2) / LLM 요약 (Phase 3)
│   ├── main.py                          # 배치 진입점
│   └── tests/
│       ├── test_skill_matcher.py
│       ├── test_wanted_crawler.py
│       └── test_normalizer.py
│
├── data/
│   ├── skills_seed.json                 # 기술 사전 시드 (100개)
│   ├── companies_seed.json              # 타겟 회사 목록
│   └── position_aliases.json            # 직무명 정규화 매핑
│
├── docs/
│   ├── AI-USAGE.md
│   ├── ARCHITECTURE.md
│   └── CRAWLING_LEGAL.md
│
└── prompts/
    └── 01-prd-creation.md
```

---

## 9. 테스트 전략

### 9.1 Spring Boot (API)

| 레벨 | 범위 | 도구 | 예시 |
|------|------|------|------|
| **단위 테스트** | Service 로직 | JUnit 5 + Mockito | `SkillRankingService`가 올바른 순위를 리턴하는지 |
| **통합 테스트** | API → DB E2E | @SpringBootTest + Testcontainers | PostgreSQL 컨테이너에서 실제 쿼리 |
| **API 테스트** | Controller 요청/응답 | MockMvc | 필터 파라미터 조합별 응답 검증 |

### 9.2 Python (배치)

| 레벨 | 범위 | 도구 | 예시 |
|------|------|------|------|
| **사전 매칭 테스트** | skill_matcher | pytest | "스프링부트" → "Spring Boot" 매핑 정확성 |
| **크롤러 테스트** | 각 크롤러 | pytest + responses (HTTP mock) | 원티드 API 응답 mock → 파싱 검증 |
| **정규화 테스트** | normalizer | pytest | "서버 개발자" → "Backend Engineer" |
| **E2E 테스트** | 크롤링→DB 저장 | pytest + Testcontainers | 실제 PostgreSQL에 INSERT 검증 |

### 9.3 키워드 추출 정확도 검증

```
1. 실제 공고 50건을 수동으로 기술 키워드 태깅 (ground truth)
2. 사전 매칭 결과와 비교
3. Precision = (정확히 추출한 수) / (추출한 총 수)
4. Recall = (정확히 추출한 수) / (실제 키워드 총 수)
5. 목표: Precision >= 0.85, Recall >= 0.75
6. 미달 시: aliases 추가, 정규표현식 패턴 개선
```

---

## 10. 모니터링 및 에러 처리

### 10.1 크롤링 모니터링

```
crawl_log 테이블로 매 실행 결과 기록:
- 성공/실패 여부
- 수집 건수 (신규/중복)
- 소요 시간
- 에러 메시지

Spring Boot AdminController에서 crawl_log 조회 API 제공.
연속 3회 실패 시 → 로그에 WARN 기록 (사이트 구조 변경 의심).
```

### 10.2 크롤러 장애 대응

| 장애 유형 | 감지 방법 | 대응 |
|----------|----------|------|
| HTTP 429 (Rate Limit) | 응답 코드 | Exponential Backoff 후 재시도 |
| HTTP 403/503 | 응답 코드 | 해당 소스 스킵, 다음 스케줄에서 재시도 |
| HTML 구조 변경 | 파싱 결과 0건 (이전에는 N건) | crawl_log에 WARN, 수동 확인 필요 플래그 |
| IP 차단 | 연속 타임아웃 | 해당 도메인 일시 중지, 수동 확인 |

### 10.3 데이터 정합성

- 중복 제거: DB unique constraint `(company_id, title_normalized, posted_date)`
- 회사명 정규화: company 테이블 기반 매핑. 매핑 실패 시 `unmatched_company` 테이블에 저장
- 개인정보 제거: 이메일(`\S+@\S+`), 전화번호(`\d{2,3}-\d{3,4}-\d{4}`) 정규표현식으로 크롤링 시점에 마스킹

---

## 11. 크롤링 법적 검토

### 11.1 원칙

| 원칙 | 설명 |
|------|------|
| **공식 API 우선** | API가 있으면 API 사용. HTML 파싱은 API 없는 경우에만 |
| **공개 데이터만** | 로그인 없이 접근 가능한 공개 페이지만 대상 |
| **robots.txt 준수** | Disallow 경로 크롤링 금지 |
| **인증 우회 금지** | CAPTCHA, 로그인, 인증 우회 없음 |
| **요청 빈도 제한** | 도메인당 1 req/sec |
| **개인정보 제거** | 수집 시점에 마스킹 |
| **용도 한정** | 개인 분석 목적. 데이터 재판매/대규모 공개 금지 |

### 11.2 참고 판례

- **사람인 vs 잡코리아 (2020)**: 무단 크롤링 **120억 손해배상**. → 잡코리아 제외.
- **hiQ Labs vs LinkedIn (2022~2026)**: Proxycurl **$500K 판결** + 서비스 종료. → LinkedIn 제외.
- **본 프로젝트**: 공식 API 우선 + 공개 데이터만 + 소량 + 개인 분석 → 리스크 매우 낮음.

---

## 12. 개발 로드맵

### Phase 0: 검증 (3일)

**목표**: "이 프로젝트로 유용한 인사이트가 나오는가?" E2E 검증

- [ ] 원티드에서 수동으로 Backend Engineer 공고 50건 수집 (CSV)
- [ ] Python 스크립트로 사전 매칭 키워드 추출
- [ ] pandas로 빈도 분석 → "Top 10 기술" 산출
- [ ] **이 결과가 수동으로 읽는 것보다 유용한지 판단**

> Phase 0의 결과가 "수동으로도 충분하다"이면, 이 프로젝트의 범위를 축소하거나 방향을 전환한다. **만들어야 하니까 만드는 것이 아니라, 유용하니까 만드는 것**이어야 한다.

### Phase 1: MVP (2주)

**목표**: 원티드 API + 사전 매칭 + Spring Boot API + Streamlit

| 주차 | 작업 | 산출물 |
|------|------|--------|
| **Week 1** | 인프라 + 크롤러 + NLP | Docker(PostgreSQL), DB 스키마(Flyway), 원티드 API 크롤러, 사전 매칭 |
| **Week 2** | Spring Boot API + Streamlit | REST API (공고 조회, 스킬 랭킹, 갭 분석), Streamlit 기본 대시보드 |

### Phase 2: 확장 (2주)

**목표**: 크롤러 추가 + 블로그 분석 + **Buzz vs Hiring Gap** + 분석 고도화

| 주차 | 작업 | 산출물 |
|------|------|--------|
| **Week 3** | 크롤러 확장 + 블로그 + 트렌드 | 점핏, Greenhouse 크롤러, 테크 블로그 RSS/HTML 수집, **GeekNews RSS 크롤러**, trend_post/trend_skill 테이블 |
| **Week 4** | 분석 고도화 + Buzz vs Hiring | 회사별 프로필, 포지션 비교, 블로그 참조 분석, **BuzzHiringGapService + TrendController**, 리포트 자동 생성 |

### Phase 3: 서비스 배포 (2주)

**목표**: React 대시보드 + 배포 + 시계열 분석 (6개월 데이터 축적 후) + HN/dev.to 확장

| 주차 | 작업 | 산출물 |
|------|------|--------|
| **Week 5** | React 대시보드 + 트렌드 확장 | Recharts 기반 시각화 (Buzz vs Hiring 2×2 차트 포함), **HN/dev.to 크롤러 추가**, 시계열 분석 |
| **Week 6** | 배포 + 문서화 | 서비스 배포, README, 기술 블로그 시리즈, 이력서 반영 |

**배포 전략**:
```
[Spring Boot API]  → Docker Image → Cloud Run / EC2 / Railway
[Python Batch]     → Docker Image → Cloud Run Job / Lambda / 로컬 cron
[PostgreSQL]       → Cloud SQL / RDS / Supabase (무료 티어)
[React Dashboard]  → Vercel / Cloudflare Pages (정적 호스팅)
```

- **MVP 배포 (비용 최소화)**: Railway (Spring Boot) + Supabase (PostgreSQL) + Vercel (React) — 무료/저가 티어 활용
- **도메인**: devpulse.kr 또는 devpulse.io (개인 프로젝트 → 서비스 전환의 증거)
- **CI/CD**: GitHub Actions → Docker Build → 자동 배포
- **인증**: Phase 3에서 Spring Security + OAuth2 (Google 로그인) 추가. Phase 1~2는 인증 없이 로컬 전용.

> **배포의 이력서 가치**: "만들어서 로컬에서만 돌렸다"와 "배포해서 다른 사람들이 실제로 쓴다"의 차이는 크다. 배포 경험은 Docker, CI/CD, 클라우드 인프라, 모니터링까지 아우르는 **운영 능력의 증거**다.

---

## 13. 이력서 표현 + 면접 대비

### 13.1 이력서 문구

```
PROJECTS

DevPulse — 개발자 채용시장 분석 서비스                    2026.03 ~
채용 공고 + 테크 블로그 데이터 기반 기술 트렌드 분석 플랫폼 (서비스 배포)
Spring Boot, Python, PostgreSQL, React, Docker, GitHub Actions

데이터 수집 파이프라인
• 원티드 API + 점핏 + 7개 빅테크 + 10개 유니콘 채용 공고 XXX건 수집
  Python 크롤러 구현, Spring Boot @Scheduled 배치 오케스트레이션
• 한/영 혼용 기술 용어 정규화 사전(100+항목) 기반 키워드 매칭으로
  채용 공고에서 기술 키워드 추출 (precision XX% — 수동 검증 50건 대비 측정 후 기입)

Spring Boot API 서버
• 기술 빈도 랭킹, 회사별 기술 프로필, 포지션 비교, 갭 분석 등
  6개 분석 API 설계 및 구현 (QueryDSL 집계 쿼리)
• Flyway 마이그레이션, Testcontainers 통합 테스트

테크 블로그 주제 분석 + 연도별 트렌드
• 네카라쿠배당토 + 주요 스타트업 11개 테크 블로그 아카이브 전체 크롤링 (2015~현재, 2,000+건)
  연도별 주제 추출 및 트렌드 분석으로 "배민의 MSA→이벤트 소싱 전환" 같은 기술 여정 가시화
• 블로그 주제와 채용 공고 키워드의 선행 패턴 발견:
  "블로그에서 집중한 기술이 1~2년 후 채용 요구에 반영" (상관 분석, 인과 미주장)

Buzz vs Hiring Gap 분석
• GeekNews 기술 뉴스와 채용 공고 키워드를 교차 비교하여
  "업계 화제 vs 실제 채용 수요" Gap 정량화 (OVERHYPED/ADOPTED/ESTABLISHED 분류)

데이터 기반 전략 도출
• 분석 결과로 Kubernetes(54%), MSA(42%) 학습 우선순위 도출,
  실제 학습 계획에 반영하여 데이터 기반 커리어 전략 수립
```

### 13.2 면접 예상 질문

| 질문 | 답변 |
|------|------|
| **왜 이 프로젝트를 했나?** | "감이 아니라 데이터로 전략을 세우고 싶었습니다. 실제로 이 분석으로 K8s와 MSA를 우선 학습하기로 결정했습니다." |
| **500건인데 왜 이 구조?** | "Phase 0에서 CSV + pandas로 먼저 검증했습니다. Python 배치와 Spring Boot API가 동시에 DB에 접근하게 되면서 SQLite의 한계가 생겨 PostgreSQL로 전환했습니다. 오버엔지니어링을 피하기 위해 병목이 생긴 시점에서 도구를 도입했습니다." |
| **왜 Spring Boot + Python?** | "크롤링과 NLP는 Python이 압도적이고, API 서빙은 제 주력인 Spring Boot로 했습니다. 도구는 문제에 맞게 선택합니다." |
| **키워드 추출 정확도는?** | "핵심은 사전 매칭입니다. 채용 공고의 기술 키워드는 대부분 영어 고유명사라서 사전에 있으면 거의 100%입니다. 수동 검증 50건 대비 precision과 recall을 측정했고, 사전 커버리지가 부족한 부분은 aliases를 추가하며 개선했습니다. **(실제 수치는 Phase 1 완료 후 기입)**" |
| **시계열 분석은 왜 안 했나?** | "500건으로 월별 트렌드를 말하는 것은 통계적으로 무의미합니다. 최소 6개월 데이터가 쌓인 후 도입할 계획이고, 현재는 스냅샷 분석에 집중했습니다." |
| **교차 분석의 한계는?** | "블로그에 없다고 그 기술을 안 쓴다고 단정할 수 없습니다. 블로그를 쓰는 팀은 전체의 일부고, NDA 때문에 못 쓰는 핵심 기술도 있습니다. 그래서 이 분석은 '참고 지표'로만 활용합니다." |
| **트래픽이 늘면?** | "현재 PostgreSQL 단일 DB입니다. 검색 쿼리가 복잡해지면 Elasticsearch를 추가할 수 있고, 혁신의 숲에서 OpenSearch 경험이 있어서 자연스럽게 전환 가능합니다." |
| **Buzz vs Hiring이 뭔가?** | "GeekNews 등 기술 커뮤니티에서 화제인 기술과, 실제 채용 공고에서 요구하는 기술의 Gap을 정량화합니다. 예를 들어 LangChain은 뉴스에서 2위지만 공고에서는 3%에 불과합니다. 반면 Kafka는 뉴스 8위인데 공고 48%입니다. 이 Gap을 모르면 유행에 끌려 비효율적으로 공부하게 됩니다." |
| **GeekNews 그냥 읽으면 되지 않나?** | "맞습니다, 매일 읽을 수도 있습니다. 하지만 30일간 247개 글에서 기술 키워드를 추출하고 채용 공고 523건과 교차 비교하는 것은 수동으로 불가능합니다. '이번 달 LangChain이 47번 언급됐는데 채용에는 16건뿐이다'라는 정량적 Gap은 자동화 없이는 알 수 없습니다." |
| **GeekNews는 1인 큐레이션 아닌가?** | "맞습니다. 그래서 이 분석을 '참고 지표'로 명시하고, Phase 2에서 Hacker News API를 추가해 소스 다변화합니다. 또한 OVERHYPED로 분류된 기술을 '안 배운다'가 아니라 '채용 빈도에 더 높은 가중치를 두고 우선순위를 정한다'는 뜻입니다." |
| **감성 분석은 왜 안 했나?** | "뉴스 제목의 감성 분석은 미해결 NLP 문제입니다. 'React 보안 취약점 발견'은 부정적이지만 React 채용에 영향을 주지 않습니다. 빈도만으로 '무엇이 화제인가'를 파악하기 충분하고, 감성은 actionable insight를 주지 않아서 의도적으로 제외했습니다." |
| **필수 vs 우대 구분은?** | "공고의 '자격요건'과 '우대사항' 섹션을 구분해서 is_required/is_preferred 태깅합니다. 빈도 분석에서 Java가 89%라고 할 때, 이 중 76%는 필수이고 13%는 우대입니다. 단순 빈도보다 필수 비율이 실질적인 채용 시그널입니다." |
| **사전에 없는 기술을 놓치면?** | "사전 매칭의 한계입니다. Recall이 100%가 아니라서, 사전에 없는 기술은 빈도가 과소 측정됩니다. 이를 보완하기 위해 미매칭 텍스트를 별도 저장하고, Phase 2에서 Kiwi 형태소 분석으로 후보를 추출합니다. 하지만 핵심 기술은 대부분 영어 고유명사라 사전 커버리지로 충분합니다." |
| **원티드와 점핏에 같은 공고가 있으면?** | "title_normalized(소문자화 + 공백 정규화 + 직무명 매핑)와 company_id, posted_date 조합으로 중복을 제거합니다. 단, 같은 포지션이 '서버 개발자'와 'Backend Engineer'로 다르게 올라올 수 있어서 직무명 정규화 매핑이 중요합니다." |
| **AI 워크플로 스킬 추적은?** | "ai_ml을 model(AI 제품 스킬)과 devtool(AI 워크플로 스킬)로 분리합니다. '한국 백엔드 공고에서 AI 도구 활용을 요구하는 비율'을 추적하면, 현재는 극소수지만 GeekNews에서 AI 관련 논의가 X%를 차지합니다. 이 Gap이 좁혀지는 시점을 데이터로 포착하는 것이 목표입니다." |
| **왜 공고를 영구 보관하나?** | "채용 공고는 마감되면 사라집니다. 한 번 수집한 데이터를 보관해야 '6개월 전에는 K8s 요구가 40%였는데 지금은 54%다' 같은 시계열 분석이 가능합니다. 공고 1건당 5~10KB라서 10,000건이 100MB — 저장 공간 문제는 없습니다." |
| **회사 카테고리는 어떻게 분류?** | "수동 시드 데이터(Big 7 + 유니콘)로 시작하고, 원티드/점핏에서 새로 발견되는 회사는 unmatched_company 테이블에 저장 후 주기적으로 수동 분류합니다. 자동 분류는 하지 않습니다 — '이 회사가 유니콘인가 스타트업인가'는 주관적 판단이 필요하기 때문입니다." |
| **블로그 연도별 트렌드의 가치는?** | "개별 블로그 글을 읽으면 '이 회사가 이런 걸 했구나'는 알 수 있지만, '이 회사가 5년간 어떤 기술적 여정을 걸었는가'는 수백 건을 통합 분석해야 보입니다. 배민이 2019~2020에 MSA 전환에 집중하고 2022부터 이벤트 소싱으로 이동한 패턴은 자동화된 주제 추출 없이는 파악이 어렵습니다." |
| **블로그→채용 선행 지표는 인과인가?** | "인과가 아니라 상관입니다. '블로그에 썼으니까 나중에 채용에 반영됐다'가 아니라, 둘 다 같은 기술 전환의 결과일 수 있습니다. 다만 '토스 블로그에 2021년부터 Kotlin이 집중 등장하고, 2023년 공고에 Kotlin 필수가 들어왔다'는 시간차 패턴 자체는 흥미로운 참고 지표입니다." |
| **블로그 요약은 어떻게?** | "Phase 2에서는 추출적 요약(제목 + 첫 문단)을 사용합니다. 기술 블로그는 제목 자체가 핵심 요약인 경우가 대부분이라 충분합니다. Phase 3에서 데이터가 쌓이면 Claude API로 정밀 요약을 생성하되, 2,000건 × $0.01 = $20 수준입니다." |
| **빅테크 vs 스타트업 분석 차이는?** | "같은 '백엔드 엔지니어'라도 빅테크은 Java/Spring 중심이고, 스타트업은 TypeScript/Go 비중이 높을 수 있습니다. 카테고리 필터로 이 차이를 정량적으로 확인하면 '나는 빅테크을 노리니까 Java 집중' 같은 전략이 가능합니다." |
| **가장 어려웠던 점은?** | "한국어 채용 공고의 기술 용어 비정형성입니다. '스프링부트', 'Spring Boot', 'SpringBoot'가 모두 같은 기술인데 다르게 표기됩니다. 정규화 사전을 구축하고 aliases를 관리하는 것이 핵심 과제였습니다." |

---

## 14. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| 원티드 API 키 거부 | 핵심 소스 상실 | 점핏 + 회사 직접으로 대체 |
| 사람인 API 개인 승인 거부 | 3순위 소스 상실 | 원티드 + 점핏으로 충분 |
| HTML 구조 변경 | 크롤러 중단 | crawl_log 모니터링 + 크롤러 플러그인 구조 |
| 기술 사전 커버리지 부족 | 키워드 추출 recall 저하 | 미매칭 키워드 리포트로 지속적 사전 확장 |
| Phase 0에서 인사이트 없음 | 프로젝트 가치 없음 | 범위 축소 또는 방향 전환. 솔직하게 판단 |
| GeekNews RSS 구조 변경 | 트렌드 수집 중단 | crawl_log 모니터링 + HN API fallback |
| Buzz vs Hiring Gap이 trivial | 트렌드 기능 가치 없음 | Phase 0에서 수동 검증. Gap이 흥미롭지 않으면 기능 축소/제외 |
| 트렌드 키워드가 기존 사전에 없음 | 매칭률 저하 | ai_ml 카테고리 + TREND scope 키워드 별도 시드 (30개) |

---

## 15. 참고 자료

### 오픈소스
- [heehehe/job-trend](https://github.com/heehehe/job-trend) — 한국 채용 트렌드 분석
- [PaulMcInnis/JobFunnel](https://github.com/PaulMcInnis/JobFunnel) — 다중 사이트 스크래퍼
- [lovit/KR-WordRank](https://github.com/lovit/KR-WordRank) — 한국어 키워드 추출
- [MaartenGr/KeyBERT](https://github.com/MaartenGr/KeyBERT) — BERT 기반 키워드 추출
- [awesome-devblog](https://github.com/awesome-devblog/awesome-devblog) — 한국 기술 블로그 목록

### API
- [원티드 OpenAPI](https://openapi.wanted.jobs/)
- [사람인 API](https://oapi.saramin.co.kr/)

### NLP
- [Kiwi (kiwipiepy)](https://github.com/bab2min/kiwipiepy)
- [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

### 법적 참고
- 사람인 vs 잡코리아 (120억 손해배상 판결)
- hiQ Labs vs LinkedIn (CFAA 판결 + $500K 합의)
