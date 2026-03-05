# DevPulse API 문서

> Base URL: `http://localhost:8080/api/v1`
> Swagger UI: `http://localhost:8080/api/swagger-ui.html`
> OpenAPI JSON: `http://localhost:8080/api/v3/api-docs`

---

## 목차

1. [채용공고](#1-채용공고)
2. [스킬 분석](#2-스킬-분석)
3. [트렌드 분석](#3-트렌드-분석)
4. [블로그 토픽 분석](#4-블로그-토픽-분석)
5. [공통 타입](#5-공통-타입)

---

## 1. 채용공고

### `GET /postings` — 채용공고 목록 조회

포지션, 회사 카테고리, 상태, 스킬, 날짜 범위 등으로 필터링하여 페이지네이션 조회.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `positionType` | `PositionType` | N | - | 포지션 필터 (`BACKEND`, `FDE`, `PRODUCT`) |
| `companyCategory` | `CompanyCategory[]` | N | - | 회사 카테고리 (복수 선택) |
| `status` | `PostingStatus[]` | N | - | 공고 상태 (`ACTIVE`, `CLOSED`) |
| `skillName` | `string[]` | N | - | 스킬명 필터 (예: `Java`, `Spring`) |
| `dateFrom` | `date` | N | - | 조회 시작일 (`yyyy-MM-dd`) |
| `dateTo` | `date` | N | - | 조회 종료일 |
| `page` | `int` | N | `0` | 페이지 번호 |
| `size` | `int` | N | `20` | 페이지 크기 |
| `sort` | `string` | N | `postedAt,desc` | 정렬 기준 |

**Response:** `Page<PostingResponse>`

```json
{
  "content": [
    {
      "id": 1,
      "title": "백엔드 개발자",
      "companyName": "토스",
      "companyCategory": "FINTECH",
      "positionType": "BACKEND",
      "experienceLevel": "3년 이상",
      "location": "서울",
      "status": "ACTIVE",
      "sourcePlatform": "wanted",
      "sourceUrl": "https://...",
      "skills": ["Java", "Spring", "Kafka"],
      "postedAt": "2026-03-01T09:00:00",
      "crawledAt": "2026-03-01T12:00:00"
    }
  ],
  "totalElements": 680,
  "totalPages": 34,
  "number": 0,
  "size": 20
}
```

---

### `GET /postings/{id}` — 채용공고 상세 조회

**Path Parameters:**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `id` | `long` | 채용공고 ID |

**Response:** `PostingDetailResponse`

```json
{
  "id": 1,
  "title": "백엔드 개발자",
  "company": {
    "id": 10,
    "name": "토스",
    "category": "FINTECH"
  },
  "positionType": "BACKEND",
  "experienceLevel": "3년 이상",
  "descriptionRaw": "...",
  "requirementsRaw": "Java 3년 이상, Spring Boot 경험",
  "preferredRaw": "Kafka, Redis 경험 우대",
  "responsibilitiesRaw": "API 서버 개발 및 운영",
  "techStackRaw": "Java, Spring Boot, Kafka",
  "benefitsRaw": "스톡옵션, 자기개발비",
  "companySize": "500명+",
  "teamInfo": "페이먼츠 팀",
  "hiringProcess": "서류 → 코딩테스트 → 면접",
  "employmentType": "정규직",
  "workType": "하이브리드",
  "location": "서울 강남",
  "salaryMin": null,
  "salaryMax": null,
  "status": "ACTIVE",
  "sourcePlatform": "wanted",
  "sourceUrl": "https://...",
  "skills": [
    {
      "id": 5,
      "name": "Java",
      "category": "language",
      "isRequired": true,
      "isPreferred": false
    }
  ],
  "postedAt": "2026-03-01T09:00:00",
  "closedAt": null,
  "crawledAt": "2026-03-01T12:00:00"
}
```

---

## 2. 스킬 분석

### `GET /analysis/skill-ranking` — 스킬 랭킹

채용공고에서 가장 많이 요구되는 기술 스택 랭킹.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `positionType` | `PositionType` | N | - | 포지션 필터 |
| `companyCategory` | `CompanyCategory[]` | N | - | 회사 카테고리 |
| `includeClosedPostings` | `boolean` | N | `false` | 마감 공고 포함 |
| `topN` | `int` | N | `20` | 상위 N개 |

**Response:** `SkillRankingResponse`

```json
{
  "snapshotDate": "2026-03-05",
  "totalPostings": 680,
  "positionType": "BACKEND",
  "rankings": [
    {
      "rank": 1,
      "skill": "Java",
      "count": 320,
      "percentage": 47.1,
      "requiredRatio": 0.85
    }
  ]
}
```

---

### `GET /analysis/company-profile/{companyId}` — 회사 프로필 (ID)

**Path Parameters:** `companyId` (long)

**Response:** `CompanyProfileResponse`

```json
{
  "companyId": 10,
  "companyName": "토스",
  "category": "FINTECH",
  "totalPostings": 45,
  "topSkills": [
    { "skill": "Java", "count": 30, "percentage": 66.7 }
  ],
  "positionBreakdown": {
    "BACKEND": 30,
    "FDE": 10,
    "PRODUCT": 5
  }
}
```

---

### `GET /analysis/company-profile?companyName={name}` — 회사 프로필 (이름)

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|-----|------|
| `companyName` | `string` | Y | 회사명 (예: `토스`, `카카오`) |

**Response:** `CompanyProfileResponse` (위와 동일)

---

### `GET /analysis/position-comparison` — 포지션 비교

2~3개 포지션의 기술 스택 비교. 공통 스킬과 포지션 고유 스킬 분석.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `positions` | `PositionType[]` | Y | - | 비교 포지션 (예: `BACKEND,FDE`) |
| `topN` | `int` | N | `20` | 포지션별 상위 N개 |

**Response:** `PositionComparisonResponse`

```json
{
  "positions": [
    {
      "positionType": "BACKEND",
      "totalPostings": 500,
      "topSkills": [
        { "rank": 1, "skill": "Java", "count": 320, "percentage": 64.0, "requiredRatio": 0.85 }
      ]
    },
    {
      "positionType": "FDE",
      "totalPostings": 150,
      "topSkills": [
        { "rank": 1, "skill": "React", "count": 120, "percentage": 80.0, "requiredRatio": 0.9 }
      ]
    }
  ],
  "commonSkills": ["TypeScript", "Git"],
  "uniqueSkills": {
    "BACKEND": ["Java", "Spring", "Kafka"],
    "FDE": ["React", "Next.js", "CSS"]
  }
}
```

---

### `POST /analysis/gap` — 갭 분석

보유 스킬과 시장 요구 스킬 비교 → 부족/강점 분석.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `positionType` | `PositionType` | N | `BACKEND` | 분석 대상 포지션 |

**Request Body:** `GapAnalysisRequest`

```json
{
  "mySkills": [
    { "name": "Java", "status": "OWNED" },
    { "name": "Kafka", "status": "LEARNING" },
    { "name": "Kubernetes", "status": "NOT_OWNED" }
  ]
}
```

> `status` enum: `OWNED` (보유), `LEARNING` (학습중), `NOT_OWNED` (미보유)

**Response:** `GapAnalysisResponse`

```json
{
  "positionType": "BACKEND",
  "matchPercentage": 65,
  "gaps": [
    {
      "skill": "Kubernetes",
      "marketRank": 5,
      "marketPercentage": 25.3,
      "userStatus": "NOT_OWNED",
      "priority": "HIGH"
    }
  ]
}
```

---

### `GET /analysis/skill-mindmap` — 스킬 마인드맵

특정 스킬의 세부 키워드를 마인드맵 형태로 조회. 채용공고에서 함께 언급되는 실무 키워드 빈도.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|-----|------|
| `skill` | `string` | Y | 스킬명 (예: `Redis`, `Kafka`) |

**Response:** `SkillMindmapResponse`

```json
{
  "skillName": "Redis",
  "nameKo": "레디스",
  "category": "database",
  "allKeywords": [
    { "keyword": "캐싱 전략", "postingCount": 45, "percentage": 60.0 },
    { "keyword": "TTL 설정", "postingCount": 30, "percentage": 40.0 }
  ],
  "keywordGroups": {
    "캐싱": [
      { "keyword": "캐싱 전략", "postingCount": 45, "percentage": 60.0 }
    ]
  },
  "totalPostingMentions": 75
}
```

---

### `GET /analysis/normalized-requirements` — 정규화된 요구사항

LLM으로 정규화된 채용 요구사항 빈도 집계.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `positionType` | `PositionType` | N | - | 포지션 필터 |
| `topN` | `int` | N | `30` | 상위 N개 |

**Response:** `NormalizedRequirementResponse`

```json
{
  "snapshotDate": "2026-03-05",
  "positionType": "BACKEND",
  "totalPostings": 500,
  "requirements": [
    {
      "rank": 1,
      "requirement": "Java 실무 경험",
      "category": "technical",
      "count": 280,
      "percentage": 56.0
    }
  ]
}
```

---

## 3. 트렌드 분석

### `GET /analysis/trend-ranking` — 트렌드 스킬 랭킹

GeekNews, HackerNews, dev.to 커뮤니티 기술 언급 빈도 랭킹.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `source` | `TrendSource` | N | 전체 | 소스 필터 (`GEEKNEWS`, `HN`, `DEVTO`) |
| `days` | `int` | N | `30` | 분석 기간 (일) |
| `topN` | `int` | N | `20` | 상위 N개 |

**Response:** `TrendRankingResponse`

```json
{
  "snapshotDate": "2026-03-05",
  "source": "GEEKNEWS",
  "period": "LAST_30_DAYS",
  "totalPosts": 247,
  "rankings": [
    { "rank": 1, "skill": "LangChain", "mentions": 47, "percentage": 19.0 },
    { "rank": 2, "skill": "Rust", "mentions": 35, "percentage": 14.2 }
  ]
}
```

---

### `GET /analysis/buzz-vs-hiring` — Buzz vs 채용 갭 분석 (2축)

커뮤니티 관심도 vs 채용 수요 비교 → 4가지 분류.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `topN` | `int` | N | `20` | 상위 N개 |
| `days` | `int` | N | `30` | 트렌드 기간 (일) |

**Response:** `BuzzHiringGapResponse`

```json
{
  "snapshotDate": "2026-03-05",
  "trendPeriod": "LAST_30_DAYS",
  "trendSource": "ALL",
  "totalTrendPosts": 247,
  "totalJobPostings": 523,
  "gaps": [
    {
      "skill": "LangChain",
      "trendMentions": 47,
      "trendRank": 1,
      "jobPostings": 16,
      "jobRank": 15,
      "jobPercentage": 3.1,
      "classification": "OVERHYPED",
      "insight": "LangChain: 커뮤니티 관심 대비 채용 수요 낮음"
    }
  ]
}
```

**Classification enum (2축):**

| 분류 | Trend | Job | 설명 |
|------|-------|-----|------|
| `ADOPTED` | HIGH (>=5%) | HIGH (>=10%) | 시장에서 채택된 기술 |
| `OVERHYPED` | HIGH | LOW | 과대평가된 기술 |
| `ESTABLISHED` | LOW | HIGH | 정착된 기술 (더 이상 화제 아님) |
| `EMERGING` | LOW | LOW | 태동기 기술 |

---

### `GET /analysis/three-axis` — 3축 분석 (Buzz + Hiring + Blog)

커뮤니티 관심도, 채용 수요, 블로그 실무 언급 3축으로 기술을 7가지로 분류.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `topN` | `int` | N | `20` | 상위 N개 |
| `days` | `int` | N | `30` | 분석 기간 (일) |

**Response:** `ThreeAxisResponse`

```json
{
  "snapshotDate": "2026-03-05",
  "period": "LAST_30_DAYS",
  "totalTrendPosts": 247,
  "totalBlogPosts": 200,
  "totalJobPostings": 523,
  "items": [
    {
      "skill": "Java",
      "trendMentions": 5,
      "trendRank": 10,
      "blogMentions": 30,
      "blogRank": 1,
      "blogPercentage": 15.0,
      "jobPostings": 465,
      "jobRank": 1,
      "jobPercentage": 88.9,
      "classification": "PRACTICAL",
      "insight": "Java: 조용히 쓰이는 기술 — 채용과 실무 블로그에서 활발"
    }
  ]
}
```

**ThreeAxisClassification enum (3축):**

| 분류 | Trend | Job | Blog | 설명 |
|------|-------|-----|------|------|
| `ADOPTED` | HIGH (>=5%) | HIGH (>=10%) | * | 시장 + 커뮤니티 모두 채택 |
| `HYPE_ONLY` | HIGH | LOW | LOW (<5%) | 과대광고 (실무 채택 미미) |
| `OVERHYPED` | HIGH | LOW | HIGH | 커뮤니티+블로그 언급 있으나 채용 수요 낮음 |
| `PRACTICAL` | LOW | HIGH | HIGH (>=5%) | 조용히 쓰이는 기술 (채용+블로그 활발) |
| `ESTABLISHED` | LOW | HIGH | LOW | 정착된 기술 |
| `BLOG_DRIVEN` | LOW | LOW | HIGH | 블로그에서만 화제 |
| `EMERGING` | LOW | LOW | LOW | 태동기 |

---

### `GET /analysis/snapshot-history` — 트렌드 스냅샷 히스토리

특정 스킬의 시간별 트렌드 순위 변화를 조회.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `source` | `TrendSource` | Y | - | 소스 (`GEEKNEWS`, `HN`, `DEVTO`) |
| `skill` | `string` | Y | - | 스킬명 (예: `React`) |
| `days` | `int` | N | `30` | 조회 기간 (일) |

**Response:** `SnapshotHistoryResponse`

```json
{
  "source": "GEEKNEWS",
  "skill": "React",
  "history": [
    { "snapshotAt": "2026-02-15T06:00:00", "rank": 1, "mentionCount": 55 },
    { "snapshotAt": "2026-02-22T06:00:00", "rank": 2, "mentionCount": 48 },
    { "snapshotAt": "2026-03-01T06:00:00", "rank": 3, "mentionCount": 42 }
  ]
}
```

---

## 4. 블로그 토픽 분석

### `GET /analysis/blog-topics/company/{companyId}` — 회사별 블로그 토픽

특정 회사의 기술 블로그 토픽 빈도 랭킹.

**Path Parameters:** `companyId` (long)

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `fromYear` | `int` | N | - | 시작 연도 |
| `toYear` | `int` | N | - | 종료 연도 |
| `topN` | `int` | N | `20` | 상위 N개 |

**Response:** `BlogTopicResponse`

```json
{
  "date": "2026-03-05",
  "companyName": "카카오",
  "companyId": 5,
  "totalPosts": 120,
  "skills": [
    { "rank": 1, "skill": "Kubernetes", "postCount": 35, "percentage": 29.2 }
  ]
}
```

---

### `GET /analysis/blog-topics/yearly-trend` — 연도별 스킬 트렌드

전체 블로그의 연도별 스킬 언급 변화.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `fromYear` | `int` | N | - | 시작 연도 |
| `toYear` | `int` | N | - | 종료 연도 |
| `topN` | `int` | N | `10` | 연도별 상위 N개 |

**Response:** `YearlyTrendResponse`

```json
{
  "date": "2026-03-05",
  "period": "2023-2026",
  "yearlyData": [
    {
      "year": 2025,
      "skills": [
        { "skill": "Kubernetes", "postCount": 80 },
        { "skill": "Kafka", "postCount": 65 }
      ]
    }
  ]
}
```

---

### `GET /analysis/blog-topics/skill/{skillName}` — 스킬별 회사 분포

특정 스킬을 블로그에서 언급하는 회사 분포.

**Path Parameters:** `skillName` (string)

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `fromYear` | `int` | N | - | 시작 연도 |
| `toYear` | `int` | N | - | 종료 연도 |

**Response:** `SkillCompanyDistributionResponse`

```json
{
  "date": "2026-03-05",
  "skillName": "Kubernetes",
  "period": "2023-2026",
  "companies": [
    { "company": "카카오", "postCount": 35 },
    { "company": "네이버", "postCount": 28 }
  ]
}
```

---

### `GET /analysis/blog-topics/posts` — 블로그 포스트 목록

기술 블로그 포스트를 최신순으로 페이지네이션 조회.

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|-----|-------|------|
| `companyId` | `long` | N | - | 회사 ID 필터 |
| `page` | `int` | N | `0` | 페이지 번호 |
| `size` | `int` | N | `20` | 페이지 크기 |

**Response:** `Page<BlogPostListResponse>`

```json
{
  "content": [
    {
      "id": 1,
      "title": "Kafka 컨슈머 최적화 사례",
      "url": "https://tech.kakao.com/...",
      "summary": "대규모 메시지 처리를 위한 컨슈머 최적화 전략을 소개합니다...",
      "companyName": "카카오",
      "publishedAt": "2026-02-28T10:00:00"
    }
  ],
  "totalElements": 350,
  "totalPages": 18,
  "number": 0,
  "size": 20
}
```

---

## 5. 공통 타입

### Enums

| Enum | 값 | 설명 |
|------|---|------|
| `PositionType` | `BACKEND`, `FDE`, `PRODUCT` | 포지션 유형 |
| `PostingStatus` | `ACTIVE`, `CLOSED`, `ARCHIVED` | 공고 상태 |
| `CompanyCategory` | `FINTECH`, `ECOMMERCE`, `SOCIAL`, `SEARCH`, `GAME`, `AI`, `SAAS`, `UNICORN`, `UNCATEGORIZED` | 회사 카테고리 |
| `TrendSource` | `GEEKNEWS`, `HN`, `DEVTO` | 트렌드 소스 |
| `Classification` | `ADOPTED`, `OVERHYPED`, `ESTABLISHED`, `EMERGING` | 2축 분류 |
| `ThreeAxisClassification` | `ADOPTED`, `OVERHYPED`, `ESTABLISHED`, `EMERGING`, `PRACTICAL`, `HYPE_ONLY`, `BLOG_DRIVEN` | 3축 분류 |
| `SkillStatus` | `OWNED`, `LEARNING`, `NOT_OWNED` | 갭 분석 스킬 보유 상태 |

### 에러 응답 (RFC 7807)

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "회사를 찾을 수 없습니다: companyId=999",
  "instance": "/api/v1/analysis/company-profile/999"
}
```

### 페이지네이션 응답

`Page<T>` 응답은 Spring Data 표준 포맷:

```json
{
  "content": [...],
  "totalElements": 680,
  "totalPages": 34,
  "number": 0,
  "size": 20,
  "first": true,
  "last": false,
  "empty": false
}
```
