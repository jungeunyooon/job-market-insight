// Enums
export type PositionType = 'BACKEND' | 'PRODUCT' | 'FDE'
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
  FDE: '데이터/인프라',
  PRODUCT: '프로덕트',
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
