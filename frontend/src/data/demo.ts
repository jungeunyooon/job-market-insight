// Demo data for DevPulse dashboard

export interface SkillRanking {
  rank: number
  skill: string
  count: number
  percentage: number
  requiredRatio: number
  change?: number // rank change vs previous period
}

export interface SkillRankingData {
  snapshotDate: string
  totalPostings: number
  positionType: string
  rankings: SkillRanking[]
}

export interface CompanyProfile {
  companyId: number
  companyName: string
  category: string
  totalPostings: number
  topSkills: { skill: string; count: number; percentage: number }[]
  positionBreakdown: Record<string, number>
}

export interface GapItem {
  skill: string
  marketRank: number
  marketPercentage: number
  userStatus: 'OWNED' | 'LEARNING' | 'NOT_OWNED'
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'CONTINUE' | 'MAINTAINED'
}

export interface JobPosting {
  id: number
  title: string
  company: string
  category: string
  position: string
  skills: string[]
  status: 'ACTIVE' | 'CLOSED' | 'EXPIRED'
  postedAt: string
  url?: string
}

export const SKILL_RANKINGS: Record<string, SkillRankingData> = {
  BACKEND: {
    snapshotDate: '2026-03-04',
    totalPostings: 523,
    positionType: 'BACKEND',
    rankings: [
      { rank: 1, skill: 'Java', count: 465, percentage: 88.9, requiredRatio: 0.76, change: 0 },
      { rank: 2, skill: 'Spring Boot', count: 429, percentage: 82.0, requiredRatio: 0.71, change: 0 },
      { rank: 3, skill: 'AWS', count: 351, percentage: 67.1, requiredRatio: 0.45, change: 1 },
      { rank: 4, skill: 'Docker', count: 319, percentage: 61.0, requiredRatio: 0.38, change: -1 },
      { rank: 5, skill: 'Kubernetes', count: 283, percentage: 54.1, requiredRatio: 0.22, change: 2 },
      { rank: 6, skill: 'MySQL', count: 267, percentage: 51.1, requiredRatio: 0.41, change: -1 },
      { rank: 7, skill: 'Kafka', count: 241, percentage: 46.1, requiredRatio: 0.18, change: 3 },
      { rank: 8, skill: 'Redis', count: 225, percentage: 43.0, requiredRatio: 0.15, change: 0 },
      { rank: 9, skill: 'PostgreSQL', count: 198, percentage: 37.9, requiredRatio: 0.20, change: 1 },
      { rank: 10, skill: 'Kotlin', count: 183, percentage: 35.0, requiredRatio: 0.25, change: 2 },
      { rank: 11, skill: 'JPA', count: 172, percentage: 32.9, requiredRatio: 0.30, change: -1 },
      { rank: 12, skill: 'Git', count: 156, percentage: 29.8, requiredRatio: 0.12, change: 0 },
      { rank: 13, skill: 'Linux', count: 141, percentage: 27.0, requiredRatio: 0.10, change: -2 },
      { rank: 14, skill: 'Elasticsearch', count: 120, percentage: 22.9, requiredRatio: 0.08, change: 0 },
      { rank: 15, skill: 'MongoDB', count: 104, percentage: 19.9, requiredRatio: 0.06, change: 1 },
    ],
  },
  FDE: {
    snapshotDate: '2026-03-04',
    totalPostings: 189,
    positionType: 'FDE',
    rankings: [
      { rank: 1, skill: 'Python', count: 162, percentage: 85.7, requiredRatio: 0.70, change: 0 },
      { rank: 2, skill: 'SQL', count: 145, percentage: 76.7, requiredRatio: 0.65, change: 0 },
      { rank: 3, skill: 'AWS', count: 132, percentage: 69.8, requiredRatio: 0.50, change: 1 },
      { rank: 4, skill: 'Spark', count: 118, percentage: 62.4, requiredRatio: 0.40, change: -1 },
      { rank: 5, skill: 'Kafka', count: 105, percentage: 55.6, requiredRatio: 0.35, change: 2 },
      { rank: 6, skill: 'Airflow', count: 95, percentage: 50.3, requiredRatio: 0.30, change: 0 },
      { rank: 7, skill: 'Docker', count: 89, percentage: 47.1, requiredRatio: 0.20, change: 0 },
      { rank: 8, skill: 'Kubernetes', count: 72, percentage: 38.1, requiredRatio: 0.15, change: 1 },
      { rank: 9, skill: 'Java', count: 65, percentage: 34.4, requiredRatio: 0.25, change: -1 },
      { rank: 10, skill: 'Hadoop', count: 58, percentage: 30.7, requiredRatio: 0.18, change: -3 },
    ],
  },
  PRODUCT: {
    snapshotDate: '2026-03-04',
    totalPostings: 247,
    positionType: 'PRODUCT',
    rankings: [
      { rank: 1, skill: 'React', count: 210, percentage: 85.0, requiredRatio: 0.72, change: 0 },
      { rank: 2, skill: 'TypeScript', count: 198, percentage: 80.2, requiredRatio: 0.68, change: 1 },
      { rank: 3, skill: 'Node.js', count: 165, percentage: 66.8, requiredRatio: 0.45, change: -1 },
      { rank: 4, skill: 'AWS', count: 142, percentage: 57.5, requiredRatio: 0.30, change: 0 },
      { rank: 5, skill: 'Docker', count: 128, percentage: 51.8, requiredRatio: 0.22, change: 1 },
      { rank: 6, skill: 'PostgreSQL', count: 115, percentage: 46.6, requiredRatio: 0.35, change: 2 },
      { rank: 7, skill: 'Next.js', count: 108, percentage: 43.7, requiredRatio: 0.28, change: 4 },
      { rank: 8, skill: 'GraphQL', count: 89, percentage: 36.0, requiredRatio: 0.15, change: -1 },
      { rank: 9, skill: 'Kotlin', count: 78, percentage: 31.6, requiredRatio: 0.20, change: 0 },
      { rank: 10, skill: 'Redis', count: 72, percentage: 29.1, requiredRatio: 0.12, change: 0 },
    ],
  },
}

export const COMPANY_PROFILES: CompanyProfile[] = [
  {
    companyId: 1,
    companyName: '네이버',
    category: 'BIGTECH',
    totalPostings: 87,
    topSkills: [
      { skill: 'Java', count: 72, percentage: 82.8 },
      { skill: 'Spring Boot', count: 65, percentage: 74.7 },
      { skill: 'Kotlin', count: 58, percentage: 66.7 },
      { skill: 'Docker', count: 52, percentage: 59.8 },
      { skill: 'Kubernetes', count: 45, percentage: 51.7 },
      { skill: 'Kafka', count: 38, percentage: 43.7 },
      { skill: 'MySQL', count: 35, percentage: 40.2 },
      { skill: 'Redis', count: 32, percentage: 36.8 },
    ],
    positionBreakdown: { BACKEND: 65, FDE: 15, PRODUCT: 7 },
  },
  {
    companyId: 2,
    companyName: '쿠팡',
    category: 'BIGTECH',
    totalPostings: 112,
    topSkills: [
      { skill: 'Java', count: 98, percentage: 87.5 },
      { skill: 'AWS', count: 95, percentage: 84.8 },
      { skill: 'Spring Boot', count: 82, percentage: 73.2 },
      { skill: 'Kotlin', count: 67, percentage: 59.8 },
      { skill: 'Docker', count: 63, percentage: 56.3 },
      { skill: 'Kafka', count: 58, percentage: 51.8 },
      { skill: 'MySQL', count: 52, percentage: 46.4 },
      { skill: 'Redis', count: 48, percentage: 42.9 },
    ],
    positionBreakdown: { BACKEND: 82, FDE: 18, PRODUCT: 12 },
  },
  {
    companyId: 3,
    companyName: '카카오',
    category: 'BIGTECH',
    totalPostings: 76,
    topSkills: [
      { skill: 'Java', count: 62, percentage: 81.6 },
      { skill: 'Spring Boot', count: 58, percentage: 76.3 },
      { skill: 'Kotlin', count: 52, percentage: 68.4 },
      { skill: 'Kubernetes', count: 42, percentage: 55.3 },
      { skill: 'AWS', count: 38, percentage: 50.0 },
      { skill: 'Kafka', count: 35, percentage: 46.1 },
      { skill: 'Redis', count: 30, percentage: 39.5 },
      { skill: 'MySQL', count: 28, percentage: 36.8 },
    ],
    positionBreakdown: { BACKEND: 52, FDE: 14, PRODUCT: 10 },
  },
  {
    companyId: 4,
    companyName: '토스',
    category: 'BIGTECH',
    totalPostings: 64,
    topSkills: [
      { skill: 'Kotlin', count: 55, percentage: 85.9 },
      { skill: 'Spring Boot', count: 52, percentage: 81.3 },
      { skill: 'Kubernetes', count: 48, percentage: 75.0 },
      { skill: 'AWS', count: 42, percentage: 65.6 },
      { skill: 'Kafka', count: 38, percentage: 59.4 },
      { skill: 'Java', count: 35, percentage: 54.7 },
      { skill: 'Redis', count: 32, percentage: 50.0 },
      { skill: 'PostgreSQL', count: 28, percentage: 43.8 },
    ],
    positionBreakdown: { BACKEND: 45, FDE: 8, PRODUCT: 11 },
  },
  {
    companyId: 5,
    companyName: '배달의민족',
    category: 'BIGTECH',
    totalPostings: 58,
    topSkills: [
      { skill: 'Java', count: 52, percentage: 89.7 },
      { skill: 'Spring Boot', count: 48, percentage: 82.8 },
      { skill: 'Kotlin', count: 35, percentage: 60.3 },
      { skill: 'AWS', count: 38, percentage: 65.5 },
      { skill: 'MySQL', count: 42, percentage: 72.4 },
      { skill: 'Kafka', count: 32, percentage: 55.2 },
      { skill: 'Redis', count: 28, percentage: 48.3 },
      { skill: 'Docker', count: 25, percentage: 43.1 },
    ],
    positionBreakdown: { BACKEND: 42, FDE: 10, PRODUCT: 6 },
  },
  {
    companyId: 6,
    companyName: '당근',
    category: 'BIGTECH',
    totalPostings: 42,
    topSkills: [
      { skill: 'Go', count: 28, percentage: 66.7 },
      { skill: 'Kubernetes', count: 32, percentage: 76.2 },
      { skill: 'gRPC', count: 22, percentage: 52.4 },
      { skill: 'Kotlin', count: 18, percentage: 42.9 },
      { skill: 'AWS', count: 35, percentage: 83.3 },
      { skill: 'Docker', count: 30, percentage: 71.4 },
      { skill: 'PostgreSQL', count: 25, percentage: 59.5 },
      { skill: 'Redis', count: 20, percentage: 47.6 },
    ],
    positionBreakdown: { BACKEND: 30, FDE: 5, PRODUCT: 7 },
  },
]

export const GAP_ANALYSIS_DATA: GapItem[] = [
  { skill: 'Java', marketRank: 1, marketPercentage: 88.9, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'Spring Boot', marketRank: 2, marketPercentage: 82.0, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'AWS', marketRank: 3, marketPercentage: 67.1, userStatus: 'LEARNING', priority: 'CONTINUE' },
  { skill: 'Docker', marketRank: 4, marketPercentage: 61.0, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'Kubernetes', marketRank: 5, marketPercentage: 54.1, userStatus: 'LEARNING', priority: 'CONTINUE' },
  { skill: 'MySQL', marketRank: 6, marketPercentage: 51.1, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'Kafka', marketRank: 7, marketPercentage: 46.1, userStatus: 'NOT_OWNED', priority: 'HIGH' },
  { skill: 'Redis', marketRank: 8, marketPercentage: 43.0, userStatus: 'NOT_OWNED', priority: 'HIGH' },
  { skill: 'PostgreSQL', marketRank: 9, marketPercentage: 37.9, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'Kotlin', marketRank: 10, marketPercentage: 35.0, userStatus: 'NOT_OWNED', priority: 'MEDIUM' },
  { skill: 'JPA', marketRank: 11, marketPercentage: 32.9, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'Git', marketRank: 12, marketPercentage: 29.8, userStatus: 'OWNED', priority: 'MAINTAINED' },
  { skill: 'Linux', marketRank: 13, marketPercentage: 27.0, userStatus: 'LEARNING', priority: 'CONTINUE' },
  { skill: 'Elasticsearch', marketRank: 14, marketPercentage: 22.9, userStatus: 'NOT_OWNED', priority: 'LOW' },
  { skill: 'MongoDB', marketRank: 15, marketPercentage: 19.9, userStatus: 'NOT_OWNED', priority: 'LOW' },
]

export const JOB_POSTINGS: JobPosting[] = [
  { id: 1, title: '백엔드 개발자', company: '네이버', category: 'BIGTECH', position: 'BACKEND', skills: ['Java', 'Spring Boot', 'Kafka', 'MySQL'], status: 'ACTIVE', postedAt: '2026-03-01' },
  { id: 2, title: '서버 엔지니어', company: '쿠팡', category: 'BIGTECH', position: 'BACKEND', skills: ['Java', 'Kotlin', 'AWS', 'Docker'], status: 'ACTIVE', postedAt: '2026-03-02' },
  { id: 3, title: '백엔드 개발자', company: '토스', category: 'BIGTECH', position: 'BACKEND', skills: ['Kotlin', 'Spring Boot', 'Kubernetes', 'Kafka'], status: 'ACTIVE', postedAt: '2026-02-28' },
  { id: 4, title: '서버 개발자', company: '당근', category: 'BIGTECH', position: 'BACKEND', skills: ['Go', 'Kubernetes', 'gRPC', 'PostgreSQL'], status: 'ACTIVE', postedAt: '2026-03-03' },
  { id: 5, title: '백엔드 엔지니어', company: '라인', category: 'BIGTECH', position: 'BACKEND', skills: ['Java', 'Spring', 'Kafka', 'Redis'], status: 'CLOSED', postedAt: '2026-02-15' },
  { id: 6, title: '프로덕트 엔지니어', company: '토스', category: 'BIGTECH', position: 'PRODUCT', skills: ['React', 'TypeScript', 'Kotlin', 'Spring Boot'], status: 'ACTIVE', postedAt: '2026-03-01' },
  { id: 7, title: '데이터 엔지니어', company: '카카오', category: 'BIGTECH', position: 'FDE', skills: ['Python', 'Spark', 'Airflow', 'Kafka'], status: 'ACTIVE', postedAt: '2026-02-25' },
  { id: 8, title: '백엔드 개발자', company: '배달의민족', category: 'BIGTECH', position: 'BACKEND', skills: ['Java', 'Spring Boot', 'MySQL', 'Redis'], status: 'ACTIVE', postedAt: '2026-03-04' },
  { id: 9, title: '서버 개발자', company: '야놀자', category: 'UNICORN', position: 'BACKEND', skills: ['Java', 'Spring Boot', 'AWS', 'Docker'], status: 'ACTIVE', postedAt: '2026-03-02' },
  { id: 10, title: '백엔드 개발자', company: '뱅크샐러드', category: 'UNICORN', position: 'BACKEND', skills: ['Kotlin', 'Spring Boot', 'Kubernetes', 'AWS'], status: 'ACTIVE', postedAt: '2026-02-27' },
  { id: 11, title: '풀스택 엔지니어', company: '리디', category: 'UNICORN', position: 'PRODUCT', skills: ['React', 'TypeScript', 'Node.js', 'PostgreSQL'], status: 'ACTIVE', postedAt: '2026-03-01' },
  { id: 12, title: '인프라 엔지니어', company: '무신사', category: 'UNICORN', position: 'FDE', skills: ['AWS', 'Docker', 'Kubernetes', 'Terraform'], status: 'CLOSED', postedAt: '2026-02-10' },
  { id: 13, title: '백엔드 개발자', company: '컬리', category: 'UNICORN', position: 'BACKEND', skills: ['Java', 'Spring Boot', 'Kafka', 'Redis'], status: 'ACTIVE', postedAt: '2026-03-03' },
  { id: 14, title: '서버 개발자', company: '센드버드', category: 'STARTUP', position: 'BACKEND', skills: ['Go', 'Kubernetes', 'gRPC', 'Redis'], status: 'ACTIVE', postedAt: '2026-02-20' },
  { id: 15, title: '백엔드 개발자', company: '채널톡', category: 'STARTUP', position: 'BACKEND', skills: ['Kotlin', 'Spring Boot', 'MongoDB', 'Redis'], status: 'ACTIVE', postedAt: '2026-03-01' },
]

// BuzzVsHiring data
export interface BuzzHiringGap {
  skill: string
  trendMentions: number
  trendRank: number
  jobPostings: number
  jobRank: number
  jobPercentage: number
  classification: 'ADOPTED' | 'OVERHYPED' | 'ESTABLISHED' | 'EMERGING'
  insight: string
}

export interface BuzzHiringData {
  snapshotDate: string
  trendPeriod: string
  totalTrendPosts: number
  totalJobPostings: number
  gaps: BuzzHiringGap[]
}

// BlogTrend data
export interface BlogTopicItem {
  rank: number
  skill: string
  postCount: number
  percentage: number
}

export interface CompanyBlogData {
  companyName: string
  companyId: number
  totalPosts: number
  skills: BlogTopicItem[]
}

export const BUZZ_HIRING_DATA: BuzzHiringData = {
  snapshotDate: '2026-03-04',
  trendPeriod: '2025-Q4 ~ 2026-Q1',
  totalTrendPosts: 18420,
  totalJobPostings: 523,
  gaps: [
    { skill: 'Kubernetes', trendMentions: 2140, trendRank: 1, jobPostings: 283, jobRank: 5, jobPercentage: 54.1, classification: 'ADOPTED', insight: '트렌드와 채용 모두 높음. 핵심 인프라 기술로 자리잡음' },
    { skill: 'Docker', trendMentions: 1980, trendRank: 2, jobPostings: 319, jobRank: 4, jobPercentage: 61.0, classification: 'ADOPTED', insight: '컨테이너화의 표준. 채용 필수 요건으로 정착' },
    { skill: 'Kafka', trendMentions: 1750, trendRank: 3, jobPostings: 241, jobRank: 7, jobPercentage: 46.1, classification: 'ADOPTED', insight: '대용량 스트리밍 처리 핵심. 대기업 중심 수요 증가' },
    { skill: 'LLM', trendMentions: 3820, trendRank: 0, jobPostings: 38, jobRank: 18, jobPercentage: 7.3, classification: 'OVERHYPED', insight: '블로그 버즈는 최고치지만 실제 채용 요구는 아직 낮음' },
    { skill: 'RAG', trendMentions: 2650, trendRank: 0, jobPostings: 22, jobRank: 22, jobPercentage: 4.2, classification: 'OVERHYPED', insight: 'AI 관심도 폭발적 증가 대비 채용 시장 아직 초기 단계' },
    { skill: 'GraphQL', trendMentions: 980, trendRank: 8, jobPostings: 65, jobRank: 14, jobPercentage: 12.4, classification: 'OVERHYPED', insight: '커뮤니티 관심 대비 실제 채용 수요는 제한적' },
    { skill: 'Java', trendMentions: 890, trendRank: 9, jobPostings: 465, jobRank: 1, jobPercentage: 88.9, classification: 'ESTABLISHED', insight: '트렌드 언급은 적지만 채용 1위 유지. 안정적 기반 기술' },
    { skill: 'Spring Boot', trendMentions: 820, trendRank: 10, jobPostings: 429, jobRank: 2, jobPercentage: 82.0, classification: 'ESTABLISHED', insight: '국내 백엔드 표준 프레임워크. 성숙기 진입' },
    { skill: 'MySQL', trendMentions: 540, trendRank: 12, jobPostings: 267, jobRank: 6, jobPercentage: 51.1, classification: 'ESTABLISHED', insight: '성숙한 RDBMS. 조용하지만 필수 스킬' },
    { skill: 'AWS', trendMentions: 1420, trendRank: 4, jobPostings: 351, jobRank: 3, jobPercentage: 67.1, classification: 'ADOPTED', insight: '클라우드 사실상 표준. 트렌드와 수요 모두 탄탄' },
    { skill: 'Rust', trendMentions: 1180, trendRank: 5, jobPostings: 18, jobRank: 25, jobPercentage: 3.4, classification: 'OVERHYPED', insight: '성능 언어로 주목받지만 국내 채용 시장 진입 초기' },
    { skill: 'Go', trendMentions: 760, trendRank: 11, jobPostings: 72, jobRank: 13, jobPercentage: 13.8, classification: 'OVERHYPED', insight: '서버 언어로 관심 증가 중이나 채용 수요는 제한적' },
    { skill: 'Terraform', trendMentions: 420, trendRank: 15, jobPostings: 98, jobRank: 11, jobPercentage: 18.7, classification: 'EMERGING', insight: 'IaC 도구로 채용 수요 꾸준히 증가 중' },
    { skill: 'Airflow', trendMentions: 380, trendRank: 16, jobPostings: 95, jobRank: 12, jobPercentage: 18.2, classification: 'EMERGING', insight: '데이터 파이프라인 필수 도구로 자리잡는 중' },
    { skill: 'Spark', trendMentions: 340, trendRank: 17, jobPostings: 118, jobRank: 10, jobPercentage: 22.6, classification: 'EMERGING', insight: '빅데이터 처리 수요 증가. 조용하지만 수요 탄탄' },
  ],
}

export const BLOG_TREND_DATA: CompanyBlogData[] = [
  {
    companyName: '네이버',
    companyId: 1,
    totalPosts: 342,
    skills: [
      { rank: 1, skill: 'Kubernetes', postCount: 58, percentage: 17.0 },
      { rank: 2, skill: 'Kafka', postCount: 45, percentage: 13.2 },
      { rank: 3, skill: 'Java', postCount: 42, percentage: 12.3 },
      { rank: 4, skill: 'LLM', postCount: 38, percentage: 11.1 },
      { rank: 5, skill: 'Spring Boot', postCount: 32, percentage: 9.4 },
      { rank: 6, skill: 'Redis', postCount: 28, percentage: 8.2 },
      { rank: 7, skill: 'Docker', postCount: 24, percentage: 7.0 },
      { rank: 8, skill: 'MySQL', postCount: 18, percentage: 5.3 },
    ],
  },
  {
    companyName: '쿠팡',
    companyId: 2,
    totalPosts: 287,
    skills: [
      { rank: 1, skill: 'Java', postCount: 62, percentage: 21.6 },
      { rank: 2, skill: 'AWS', postCount: 55, percentage: 19.2 },
      { rank: 3, skill: 'Kafka', postCount: 48, percentage: 16.7 },
      { rank: 4, skill: 'Kubernetes', postCount: 38, percentage: 13.2 },
      { rank: 5, skill: 'Spring Boot', postCount: 32, percentage: 11.1 },
      { rank: 6, skill: 'Docker', postCount: 25, percentage: 8.7 },
      { rank: 7, skill: 'MySQL', postCount: 18, percentage: 6.3 },
      { rank: 8, skill: 'Redis', postCount: 15, percentage: 5.2 },
    ],
  },
  {
    companyName: '카카오',
    companyId: 3,
    totalPosts: 315,
    skills: [
      { rank: 1, skill: 'LLM', postCount: 72, percentage: 22.9 },
      { rank: 2, skill: 'Kotlin', postCount: 55, percentage: 17.5 },
      { rank: 3, skill: 'Kubernetes', postCount: 42, percentage: 13.3 },
      { rank: 4, skill: 'Spring Boot', postCount: 38, percentage: 12.1 },
      { rank: 5, skill: 'RAG', postCount: 32, percentage: 10.2 },
      { rank: 6, skill: 'Kafka', postCount: 28, percentage: 8.9 },
      { rank: 7, skill: 'Redis', postCount: 22, percentage: 7.0 },
      { rank: 8, skill: 'MySQL', postCount: 16, percentage: 5.1 },
    ],
  },
  {
    companyName: '토스',
    companyId: 4,
    totalPosts: 198,
    skills: [
      { rank: 1, skill: 'Kotlin', postCount: 52, percentage: 26.3 },
      { rank: 2, skill: 'Spring Boot', postCount: 42, percentage: 21.2 },
      { rank: 3, skill: 'Kubernetes', postCount: 35, percentage: 17.7 },
      { rank: 4, skill: 'LLM', postCount: 28, percentage: 14.1 },
      { rank: 5, skill: 'AWS', postCount: 22, percentage: 11.1 },
      { rank: 6, skill: 'Kafka', postCount: 18, percentage: 9.1 },
      { rank: 7, skill: 'PostgreSQL', postCount: 12, percentage: 6.1 },
      { rank: 8, skill: 'Redis', postCount: 10, percentage: 5.1 },
    ],
  },
  {
    companyName: '당근',
    companyId: 6,
    totalPosts: 156,
    skills: [
      { rank: 1, skill: 'Go', postCount: 48, percentage: 30.8 },
      { rank: 2, skill: 'Kubernetes', postCount: 38, percentage: 24.4 },
      { rank: 3, skill: 'gRPC', postCount: 28, percentage: 17.9 },
      { rank: 4, skill: 'AWS', postCount: 22, percentage: 14.1 },
      { rank: 5, skill: 'PostgreSQL', postCount: 15, percentage: 9.6 },
      { rank: 6, skill: 'Docker', postCount: 12, percentage: 7.7 },
      { rank: 7, skill: 'Redis', postCount: 10, percentage: 6.4 },
      { rank: 8, skill: 'Rust', postCount: 8, percentage: 5.1 },
    ],
  },
]

// Buzz vs Hiring scatter data
export interface BuzzHiringItem {
  skill: string
  trendScore: number   // 0-100 (X axis: trend/buzz %)
  jobScore: number     // 0-100 (Y axis: job posting %)
  quadrant: 'OVERHYPED' | 'ADOPTED' | 'ESTABLISHED' | 'EMERGING'
  category: string
}

export const BUZZ_VS_HIRING: BuzzHiringItem[] = [
  { skill: 'Rust', trendScore: 45, jobScore: 5, quadrant: 'OVERHYPED', category: 'language' },
  { skill: 'WebAssembly', trendScore: 30, jobScore: 3, quadrant: 'OVERHYPED', category: 'concept' },
  { skill: 'Deno', trendScore: 20, jobScore: 2, quadrant: 'OVERHYPED', category: 'framework' },
  { skill: 'React', trendScore: 35, jobScore: 65, quadrant: 'ADOPTED', category: 'framework' },
  { skill: 'TypeScript', trendScore: 40, jobScore: 58, quadrant: 'ADOPTED', category: 'language' },
  { skill: 'Kubernetes', trendScore: 28, jobScore: 42, quadrant: 'ADOPTED', category: 'devops' },
  { skill: 'Docker', trendScore: 15, jobScore: 72, quadrant: 'ADOPTED', category: 'devops' },
  { skill: 'Spring Boot', trendScore: 8, jobScore: 55, quadrant: 'ESTABLISHED', category: 'framework' },
  { skill: 'Java', trendScore: 5, jobScore: 68, quadrant: 'ESTABLISHED', category: 'language' },
  { skill: 'MySQL', trendScore: 3, jobScore: 52, quadrant: 'ESTABLISHED', category: 'database' },
  { skill: 'PostgreSQL', trendScore: 12, jobScore: 45, quadrant: 'ESTABLISHED', category: 'database' },
  { skill: 'Redis', trendScore: 7, jobScore: 38, quadrant: 'ESTABLISHED', category: 'database' },
  { skill: 'LangChain', trendScore: 55, jobScore: 8, quadrant: 'OVERHYPED', category: 'ai_ml_devtool' },
  { skill: 'GPT API', trendScore: 60, jobScore: 15, quadrant: 'ADOPTED', category: 'ai_ml_model' },
  { skill: 'Kafka', trendScore: 10, jobScore: 35, quadrant: 'ESTABLISHED', category: 'messaging' },
  { skill: 'Next.js', trendScore: 25, jobScore: 22, quadrant: 'ADOPTED', category: 'framework' },
  { skill: 'Flutter', trendScore: 18, jobScore: 12, quadrant: 'ADOPTED', category: 'framework' },
  { skill: 'Go', trendScore: 22, jobScore: 18, quadrant: 'ADOPTED', category: 'language' },
  { skill: 'Terraform', trendScore: 15, jobScore: 20, quadrant: 'ADOPTED', category: 'devops' },
  { skill: 'MLflow', trendScore: 12, jobScore: 4, quadrant: 'EMERGING', category: 'ai_ml_devtool' },
]

// Blog trend data (yearly)
export interface BlogTrendItem {
  year: number
  skills: Record<string, number>  // skill name → post count
}

export const BLOG_TRENDS: BlogTrendItem[] = [
  { year: 2022, skills: { 'Kubernetes': 45, 'Docker': 38, 'Kafka': 22, 'Spring Boot': 30, 'React': 25, 'GPT API': 2 } },
  { year: 2023, skills: { 'Kubernetes': 52, 'Docker': 35, 'Kafka': 28, 'Spring Boot': 33, 'React': 30, 'GPT API': 18 } },
  { year: 2024, skills: { 'Kubernetes': 58, 'Docker': 32, 'Kafka': 35, 'Spring Boot': 28, 'React': 32, 'GPT API': 45 } },
  { year: 2025, skills: { 'Kubernetes': 62, 'Docker': 30, 'Kafka': 40, 'Spring Boot': 25, 'React': 28, 'GPT API': 65 } },
]

export const BLOG_TREND_COMPANIES = ['네이버', '카카오', '배달의민족', '당근', '쿠팡'] as const

export const POSITIONS = ['BACKEND', 'FDE', 'PRODUCT'] as const
export type PositionType = (typeof POSITIONS)[number]

export const CATEGORIES = ['BIGTECH', 'BIGTECH_SUB', 'UNICORN', 'STARTUP', 'SI', 'MID'] as const

export const CATEGORY_LABELS: Record<string, string> = {
  BIGTECH: '빅테크',
  BIGTECH_SUB: '대기업 자회사',
  UNICORN: '유니콘',
  STARTUP: '스타트업',
  SI: 'SI',
  MID: '중견',
}

export const POSITION_LABELS: Record<string, string> = {
  BACKEND: '백엔드',
  FDE: '데이터/인프라',
  PRODUCT: '프로덕트',
}

export const STATUS_LABELS: Record<string, string> = {
  ACTIVE: '채용중',
  CLOSED: '마감',
  EXPIRED: '만료',
}
