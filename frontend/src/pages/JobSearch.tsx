import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, ExternalLink } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { SkillPill } from '@/components/ui/SkillPill'
import {
  JOB_POSTINGS, POSITION_LABELS, CATEGORY_LABELS, STATUS_LABELS,
  CATEGORIES, POSITIONS, type PositionType,
} from '@/data/demo'

export function JobSearch() {
  const [search, setSearch] = useState('')
  const [positionFilter, setPositionFilter] = useState<PositionType | ''>('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('ACTIVE')

  const filtered = useMemo(() => {
    return JOB_POSTINGS.filter((p) => {
      if (search && !p.title.toLowerCase().includes(search.toLowerCase()) && !p.company.toLowerCase().includes(search.toLowerCase()) && !p.skills.some((s) => s.toLowerCase().includes(search.toLowerCase()))) return false
      if (positionFilter && p.position !== positionFilter) return false
      if (categoryFilter && p.category !== categoryFilter) return false
      if (statusFilter && p.status !== statusFilter) return false
      return true
    })
  }, [search, positionFilter, categoryFilter, statusFilter])

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
              onChange={(e) => setSearch(e.target.value)}
              placeholder="키워드, 회사명, 스킬로 검색..."
              className="w-full rounded-lg border border-border-default bg-bg-base py-2.5 pl-10 pr-4 text-sm text-text-primary placeholder-text-subtle outline-none transition-colors focus:border-accent-blue"
            />
          </div>
          <Filter className="h-4 w-4 text-text-subtle" />
        </div>
        <div className="mt-3 flex flex-wrap gap-3">
          <select
            value={positionFilter}
            onChange={(e) => setPositionFilter(e.target.value as PositionType | '')}
            className="rounded-lg border border-border-default bg-bg-base px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">전체 포지션</option>
            {POSITIONS.map((pos) => (
              <option key={pos} value={pos}>{POSITION_LABELS[pos]}</option>
            ))}
          </select>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="rounded-lg border border-border-default bg-bg-base px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">전체 카테고리</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{CATEGORY_LABELS[cat]}</option>
            ))}
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-border-default bg-bg-base px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">전체 상태</option>
            <option value="ACTIVE">채용중</option>
            <option value="CLOSED">마감</option>
            <option value="EXPIRED">만료</option>
          </select>
        </div>
      </div>

      {/* Results count */}
      <div className="mb-4 text-sm text-text-muted">
        총 <span className="font-mono font-medium text-text-primary">{filtered.length}</span>건
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
            {filtered.map((posting) => (
              <tr key={posting.id} className="border-b border-border-muted transition-colors hover:bg-bg-elevated group">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium">{posting.title}</span>
                    <ExternalLink className="h-3 w-3 text-text-subtle opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span>{posting.company}</span>
                    <Badge>{CATEGORY_LABELS[posting.category]}</Badge>
                  </div>
                </td>
                <td className="px-4 py-3 text-text-muted">
                  {POSITION_LABELS[posting.position] || posting.position}
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
                    {STATUS_LABELS[posting.status]}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right font-mono text-xs text-text-muted">
                  {posting.postedAt}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-text-muted">
                  검색 결과가 없습니다
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}
