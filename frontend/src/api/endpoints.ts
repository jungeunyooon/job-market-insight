import { get, post } from './client'
import type {
  Page,
  PostingResponse,
  PostingDetailResponse,
  SkillRankingResponse,
  SkillKeywordResponse,
  SkillMindmapResponse,
  CompanyProfileResponse,
  PositionComparisonResponse,
  GapAnalysisRequest,
  GapAnalysisResponse,
  TrendRankingResponse,
  BuzzHiringGapResponse,
  BlogTopicResponse,
  YearlyTrendResponse,
  SkillCompanyDistributionResponse,
  PositionType,
  CompanyCategory,
  PostingStatus,
  TrendSource,
} from './types'

// --- Postings ---
export function getPostings(params?: {
  positionType?: PositionType
  companyCategory?: CompanyCategory
  status?: PostingStatus
  skillName?: string
  dateFrom?: string
  dateTo?: string
  page?: number
  size?: number
}) {
  return get<Page<PostingResponse>>('/postings', params)
}

export function getPostingDetail(id: number) {
  return get<PostingDetailResponse>(`/postings/${id}`)
}

// --- Analysis ---
export function getSkillRanking(params?: {
  positionType?: PositionType
  companyCategory?: CompanyCategory
  includeClosedPostings?: boolean
  topN?: number
}) {
  return get<SkillRankingResponse>('/analysis/skill-ranking', params)
}

export function getCompanyProfile(companyId: number) {
  return get<CompanyProfileResponse>(`/analysis/company-profile/${companyId}`)
}

export function getCompanyProfileByName(companyName: string) {
  return get<CompanyProfileResponse>('/analysis/company-profile', { companyName })
}

export function getPositionComparison(positions: PositionType[], topN = 20) {
  const params = new URLSearchParams()
  positions.forEach((p) => params.append('positions', p))
  params.set('topN', String(topN))
  return get<PositionComparisonResponse>(`/analysis/position-comparison?${params.toString()}`)
}

export function analyzeGap(request: GapAnalysisRequest, positionType: PositionType = 'BACKEND') {
  return post<GapAnalysisResponse>(`/analysis/gap?positionType=${positionType}`, request)
}

// --- Skill Keywords & Mindmap ---
export function getSkillKeywords(skillId: number) {
  return get<SkillKeywordResponse>(`/skills/${skillId}/keywords`)
}

export function getSkillMindmap(skillName: string) {
  return get<SkillMindmapResponse>('/analysis/skill-mindmap', { skill: skillName })
}

// --- Trends ---
export function getTrendRanking(params?: {
  source?: TrendSource
  days?: number
  topN?: number
}) {
  return get<TrendRankingResponse>('/analysis/trend-ranking', params)
}

export function getBuzzVsHiring(params?: {
  topN?: number
  days?: number
}) {
  return get<BuzzHiringGapResponse>('/analysis/buzz-vs-hiring', params)
}

// --- Blog Topics ---
export function getCompanyBlogTopics(companyId: number, params?: {
  fromYear?: number
  toYear?: number
  topN?: number
}) {
  return get<BlogTopicResponse>(`/analysis/blog-topics/company/${companyId}`, params)
}

export function getYearlySkillTrend(params?: {
  fromYear?: number
  toYear?: number
  topN?: number
}) {
  return get<YearlyTrendResponse>('/analysis/blog-topics/yearly-trend', params)
}

export function getSkillCompanyDistribution(skillName: string, params?: {
  fromYear?: number
  toYear?: number
}) {
  return get<SkillCompanyDistributionResponse>(`/analysis/blog-topics/skill/${skillName}`, params)
}
