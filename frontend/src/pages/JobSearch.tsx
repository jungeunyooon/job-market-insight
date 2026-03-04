import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, ExternalLink, ChevronLeft, ChevronRight } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { SkillPill } from '@/components/ui/SkillPill'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useApi } from '@/hooks/useApi'
import { getPostings } from '@/api/endpoints'
import {
  POSITION_LABELS, CATEGORY_LABELS, STATUS_LABELS,
  type PositionType, type CompanyCategory, type PostingStatus,
} from '@/api/types'

const POSITIONS: PositionType[] = ['BACKEND', 'FDE', 'PRODUCT']
const CATEGORIES: CompanyCategory[] = ['BIGTECH', 'BIGTECH_SUB', 'UNICORN', 'STARTUP', 'SI', 'MID']

export function JobSearch() {
  const [search, setSearch] = useState('')
  const [positionFilter, setPositionFilter] = useState<PositionType | ''>('')
  const [categoryFilter, setCategoryFilter] = useState<CompanyCategory | ''>('')
  const [statusFilter, setStatusFilter] = useState<PostingStatus | ''>('ACTIVE')
  const [page, setPage] = useState(0)

  const { data, loading, error, refetch } = useApi(
    () => getPostings({
      positionType: positionFilter || undefined,
      companyCategory: categoryFilter || undefined,
      status: statusFilter || undefined,
      skillName: search || undefined,
      page,
      size: 20,
    }),
    [positionFilter, categoryFilter, statusFilter, search, page],
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">채용공고 검색</h2>
        <p className="mt-1 text-sm text-text-muted">
          필터를 적용하여 채용공고를 검색합니다
        </p>
      </div>

      {/* Search & Filters */}
      <div className="mb-6 rounded-xl border border-border-default bg-bg-surface p-4">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-subtle" />
            <input
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0) }}
              placeholder="스킬명으로 검색..."
              className="w-full rounded-lg border border-border-default bg-bg-base py-2.5 pl-10 pr-4 text-sm text-text-primary placeholder-text-subtle outline-none transition-colors focus:border-accent-blue"
            />
          </div>
          <Filter className="h-4 w-4 text-text-subtle" />
        </div>
        <div className="mt-3 flex flex-wrap gap-3">
          <select
            value={positionFilter}
            onChange={(e) => { setPositionFilter(e.target.value as PositionType | ''); setPage(0) }}
            className="rounded-lg border border-border-default bg-bg-base px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">전체 포지션</option>
            {POSITIONS.map((pos) => (
              <option key={pos} value={pos}>{POSITION_LABELS[pos]}</option>
            ))}
          </select>
          <select
            value={categoryFilter}
            onChange={(e) => { setCategoryFilter(e.target.value as CompanyCategory | ''); setPage(0) }}
            className="rounded-lg border border-border-default bg-bg-base px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">전체 카테고리</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{CATEGORY_LABELS[cat]}</option>
            ))}
          </select>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value as PostingStatus | ''); setPage(0) }}
            className="rounded-lg border border-border-default bg-bg-base px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">전체 상태</option>
            <option value="ACTIVE">채용중</option>
            <option value="CLOSED">마감</option>
            <option value="EXPIRED">만료</option>
          </select>
        </div>
      </div>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <>
          {/* Results count */}
          <div className="mb-4 flex items-center justify-between text-sm text-text-muted">
            <span>총 <span className="font-mono font-medium text-text-primary">{data.totalElements}</span>건</span>
            <span>{data.number + 1} / {data.totalPages} 페이지</span>
          </div>

          {/* Table */}
          <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border-default bg-bg-elevated text-text-muted">
                  <th className="px-4 py-3 text-left font-medium">공고</th>
                  <th className="px-4 py-3 text-left font-medium">회사</th>
                  <th className="px-4 py-3 text-left font-medium">포지션</th>
                  <th className="px-4 py-3 text-left font-medium">기술 스택</th>
                  <th className="px-4 py-3 text-center font-medium">상태</th>
                  <th className="px-4 py-3 text-right font-medium">등록일</th>
                </tr>
              </thead>
              <tbody>
                {data.content.map((posting) => (
                  <tr key={posting.id} className="border-b border-border-muted transition-colors hover:bg-bg-elevated group">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <span className="font-medium">{posting.title}</span>
                        {posting.sourceUrl && (
                          <a href={posting.sourceUrl} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3 text-text-subtle opacity-0 transition-opacity group-hover:opacity-100" />
                          </a>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span>{posting.companyName}</span>
                        <Badge>{CATEGORY_LABELS[posting.companyCategory] || posting.companyCategory}</Badge>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-text-muted">
                      {POSITION_LABELS[posting.positionType] || posting.positionType}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {posting.skills.map((skill) => (
                          <SkillPill key={skill} name={skill} />
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={posting.status === 'ACTIVE' ? 'active' : 'closed'}>
                        {STATUS_LABELS[posting.status] || posting.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-xs text-text-muted">
                      {posting.postedAt?.split('T')[0]}
                    </td>
                  </tr>
                ))}
                {data.content.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-text-muted">
                      검색 결과가 없습니다
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data.totalPages > 1 && (
            <div className="mt-4 flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={data.first}
                className="rounded-lg border border-border-default px-3 py-2 text-sm transition-colors hover:bg-bg-elevated disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="px-3 text-sm font-mono text-text-muted">
                {data.number + 1} / {data.totalPages}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={data.last}
                className="rounded-lg border border-border-default px-3 py-2 text-sm transition-colors hover:bg-bg-elevated disabled:opacity-40"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </>
      )}
    </motion.div>
  )
}
