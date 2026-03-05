// Enums
export type PositionType = 'BACKEND' | 'FRONTEND' | 'FULLSTACK' | 'PRODUCT' | 'FDE' | 'DATA_ENGINEER' | 'DEVOPS' | 'ML_AI' | 'MOBILE' | 'QA' | 'SECURITY'
export type CompanyCategory = 'BIGTECH' | 'BIGTECH_SUB' | 'UNICORN' | 'STARTUP' | 'SI' | 'MID' | 'FINANCE' | 'UNCATEGORIZED'
export type PostingStatus = 'ACTIVE' | 'CLOSED' | 'EXPIRED' | 'ARCHIVED'
export type TrendSource = 'GEEKNEWS' | 'HN' | 'DEVTO'
export type SkillStatus = 'OWNED' | 'LEARNING' | 'NOT_OWNED'
export type Classification = 'OVERHYPED' | 'ADOPTED' | 'ESTABLISHED' | 'EMERGING'
export type GapPriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'CONTINUE' | 'MAINTAINED'

// --- Posting ---
export interface PostingResponse {
  id: number
  title: string
  companyName: string
  companyCategory: CompanyCategory
  positionType: PositionType
  experienceLevel: string
  location: string
  status: PostingStatus
  sourcePlatform: string
  sourceUrl: string
  skills: string[]
  postedAt: string
  crawledAt: string
}

export interface PostingDetailResponse {
  id: number
  title: string
  company: { id: number; name: string; category: CompanyCategory }
  positionType: PositionType
  experienceLevel: string
  descriptionRaw: string
  requirementsRaw: string | null
  preferredRaw: string | null
  responsibilitiesRaw: string | null
  techStackRaw: string | null
  benefitsRaw: string | null
  companySize: string | null
  teamInfo: string | null
  hiringProcess: string | null
  employmentType: string | null
  workType: string | null
  location: string
  salaryMin: number | null
  salaryMax: number | null
  status: PostingStatus
  sourcePlatform: string
  sourceUrl: string
  skills: { id: number; name: string; category: string; isRequired: boolean; isPreferred: boolean }[]
  postedAt: string
  closedAt: string | null
  crawledAt: string
}

// --- Analysis ---
export interface SkillRankItem {
  rank: number
  skill: string
  count: number
  percentage: number
  requiredRatio: number
}

export interface SkillRankingResponse {
  snapshotDate: string
  totalPostings: number
  positionType: PositionType
  rankings: SkillRankItem[]
}

export interface SkillUsage {
  skill: string
  count: number
  percentage: number
}

export interface CompanyProfileResponse {
  companyId: number
  companyName: string
  category: CompanyCategory
  totalPostings: number
  topSkills: SkillUsage[]
  positionBreakdown: Record<string, number>
}

export interface PositionSkillProfile {
  positionType: PositionType
  totalPostings: number
  topSkills: SkillRankItem[]
}

export interface PositionComparisonResponse {
  positions: PositionSkillProfile[]
  commonSkills: string[]
  uniqueSkills: Record<string, string[]>
}

export interface UserSkill {
  name: string
  status: SkillStatus
}

export interface GapAnalysisRequest {
  mySkills: UserSkill[]
}

export interface SkillGap {
  skill: string
  marketRank: number
  marketPercentage: number
  userStatus: string
  priority: string
}

export interface GapAnalysisResponse {
  positionType: PositionType
  matchPercentage: number
  gaps: SkillGap[]
}

// --- Trend ---
export interface TrendRankItem {
  rank: number
  skill: string
  mentions: number
  percentage: number
}

export interface TrendRankingResponse {
  snapshotDate: string
  source: string
  period: string
  totalPosts: number
  rankings: TrendRankItem[]
}

export interface BuzzHiringGap {
  skill: string
  trendMentions: number
  trendRank: number
  jobPostings: number
  jobRank: number
  jobPercentage: number
  classification: Classification
  insight: string
}

export interface BuzzHiringGapResponse {
  snapshotDate: string
  trendPeriod: string
  trendSource: string
  totalTrendPosts: number
  totalJobPostings: number
  gaps: BuzzHiringGap[]
}

// --- Three-Axis Analysis ---
export type ThreeAxisClassification =
  | 'ADOPTED' | 'OVERHYPED' | 'ESTABLISHED' | 'EMERGING'
  | 'PRACTICAL' | 'HYPE_ONLY' | 'BLOG_DRIVEN'

export interface ThreeAxisItem {
  skill: string
  trendMentions: number
  trendRank: number
  blogMentions: number
  blogRank: number
  blogPercentage: number
  jobPostings: number
  jobRank: number
  jobPercentage: number
  classification: ThreeAxisClassification
  insight: string
}

export interface ThreeAxisResponse {
  snapshotDate: string
  period: string
  totalTrendPosts: number
  totalBlogPosts: number
  totalJobPostings: number
  items: ThreeAxisItem[]
}

// --- Snapshot History ---
export interface SnapshotPoint {
  snapshotAt: string
  rank: number
  mentionCount: number
}

export interface SnapshotHistoryResponse {
  source: string
  skill: string
  history: SnapshotPoint[]
}

// --- Blog ---
export interface BlogTopicItem {
  rank: number
  skill: string
  postCount: number
  percentage: number
}

export interface BlogTopicResponse {
  date: string
  companyName: string
  companyId: number
  totalPosts: number
  skills: BlogTopicItem[]
}

export interface YearlySkillData {
  year: number
  skills: { skill: string; postCount: number }[]
}

export interface YearlyTrendResponse {
  date: string
  period: string
  yearlyData: YearlySkillData[]
}

export interface SkillCompanyDistributionResponse {
  date: string
  skillName: string
  period: string
  companies: { company: string; postCount: number }[]
}

// --- Blog Post List ---
export interface BlogPostListResponse {
  id: number
  title: string
  url: string
  summary: string | null
  companyName: string
  publishedAt: string
}

// --- Skill Keyword ---
export interface KeywordFrequency {
  keyword: string
  frequency: number
}

export interface SkillKeywordResponse {
  skillName: string
  category: string
  keywords: KeywordFrequency[]
  totalPostings: number
}

// --- Skill Mindmap ---
export interface KeywordNode {
  keyword: string
  postingCount: number
  percentage: number
}

export interface SkillMindmapResponse {
  skillName: string
  nameKo: string
  category: string
  allKeywords: KeywordNode[]
  keywordGroups: Record<string, KeywordNode[]>
  totalPostingMentions: number
}

// --- Pagination (Spring Page) ---
export interface Page<T> {
  content: T[]
  totalElements: number
  totalPages: number
  size: number
  number: number
  first: boolean
  last: boolean
  empty: boolean
}

// --- Labels ---
export const POSITION_LABELS: Record<string, string> = {
  BACKEND: '백엔드',
  FRONTEND: '프론트엔드',
  FULLSTACK: '풀스택',
  PRODUCT: '프로덕트',
  FDE: 'FDE',
  DATA_ENGINEER: '데이터 엔지니어',
  DEVOPS: 'DevOps/인프라',
  ML_AI: 'ML/AI',
  MOBILE: '모바일',
  QA: 'QA',
  SECURITY: '보안',
}

export const CATEGORY_LABELS: Record<string, string> = {
  BIGTECH: '빅테크',
  BIGTECH_SUB: '대기업 자회사',
  UNICORN: '유니콘',
  STARTUP: '스타트업',
  SI: 'SI',
  MID: '중견',
  FINANCE: '금융',
  UNCATEGORIZED: '미분류',
}

export const STATUS_LABELS: Record<string, string> = {
  ACTIVE: '채용중',
  CLOSED: '마감',
  EXPIRED: '만료',
  ARCHIVED: '보관',
}
