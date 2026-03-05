import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
  BarChart, Bar, Cell,
} from 'recharts'
import { BookOpen, ExternalLink } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { getYearlySkillTrend, getBlogPosts, getSkillMindmap } from '@/api/endpoints'

const CHART_COLORS = [
  '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948',
  '#b07aa1', '#ff9da7', '#9c755f', '#bab0ab',
]

export function BlogTrend() {
  const chart = useChartStyles()

  const { data, loading, error, refetch } = useApi(
    () => getYearlySkillTrend({ topN: 10 }),
    [],
  )

  const { data: postsData } = useApi(() => getBlogPosts({ size: 10 }), [])

  // Derive all skill names from yearlyData
  const allSkills = useMemo(() => {
    if (!data?.yearlyData) return []
    const set = new Set<string>()
    data.yearlyData.forEach((y) => y.skills.forEach((s) => set.add(s.skill)))
    return Array.from(set)
  }, [data])

  const [activeSkills, setActiveSkills] = useState<Set<string> | null>(null)
  const [selectedSkillForKeywords, setSelectedSkillForKeywords] = useState<string | null>(null)

  // Fetch keyword mindmap for the selected skill
  const { data: mindmapData, loading: mindmapLoading } = useApi(
    () => selectedSkillForKeywords
      ? getSkillMindmap(selectedSkillForKeywords)
      : Promise.resolve(null as never),
    [selectedSkillForKeywords],
  )

  // Initialize activeSkills once data is loaded
  const currentActive = activeSkills ?? new Set(allSkills)

  // Build flat chart data: [{ year: '2022', Kubernetes: 45, ... }, ...]
  const chartData = useMemo(() => {
    if (!data?.yearlyData) return []
    return data.yearlyData.map((row) => {
      const point: Record<string, number | string> = { year: String(row.year) }
      for (const s of row.skills) {
        if (currentActive.has(s.skill)) {
          point[s.skill] = s.postCount
        }
      }
      return point
    })
  }, [data, currentActive])

  if (loading) return <LoadingState />
  if (error || !data) return <ErrorState message={error || '데이터를 불러올 수 없습니다'} onRetry={refetch} />

  const totalPosts = data.yearlyData.reduce(
    (sum, row) => sum + row.skills.reduce((a, s) => a + s.postCount, 0), 0,
  )
  const yearsCount = data.yearlyData.length

  function toggleSkill(skill: string) {
    setActiveSkills((prev) => {
      const next = new Set(prev ?? allSkills)
      if (next.has(skill)) {
        if (next.size > 1) next.delete(skill)
      } else {
        next.add(skill)
      }
      return next
    })
  }

  function toggleAll() {
    if (currentActive.size === allSkills.length) {
      setActiveSkills(new Set([allSkills[0]]))
    } else {
      setActiveSkills(new Set(allSkills))
    }
  }

  function handleSkillChipClick(skill: string) {
    toggleSkill(skill)
    setSelectedSkillForKeywords(skill)
  }

  // Keyword bar data from mindmap
  const keywordBarData = useMemo(() => {
    if (!mindmapData?.allKeywords) return []
    return mindmapData.allKeywords.slice(0, 15).map((kw, i) => ({
      keyword: kw.keyword,
      count: kw.postingCount,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    }))
  }, [mindmapData])

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">블로그 트렌드</h2>
        <p className="mt-1 text-sm text-text-muted">
          기술 블로그 연도별 스킬 언급 추이
        </p>
      </div>

      <div className="mb-6 grid grid-cols-3 gap-4">
        <KpiCard label="총 블로그 포스트" value={totalPosts.toLocaleString()} icon={<BookOpen className="h-5 w-5" />} />
        <KpiCard label="분석 스킬 수" value={allSkills.length} />
        <KpiCard label="분석 연도" value={`${yearsCount}년`} />
      </div>

      {/* Skill filter — chip toggle */}
      <div className="mb-6 rounded-xl border border-border-default bg-bg-surface px-5 py-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm font-medium text-text-primary">스킬 필터</span>
          <button onClick={toggleAll} className="text-xs text-accent-blue hover:underline">
            {currentActive.size === allSkills.length ? '전체 해제' : '전체 선택'}
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {allSkills.map((skill, idx) => {
            const color = CHART_COLORS[idx % CHART_COLORS.length]
            const active = currentActive.has(skill)
            const isKeywordSelected = selectedSkillForKeywords === skill
            return (
              <button
                key={skill}
                onClick={() => handleSkillChipClick(skill)}
                className={`cursor-pointer rounded-full px-3.5 py-1.5 text-xs font-medium font-mono transition-all ${
                  active
                    ? 'text-white shadow-sm'
                    : 'bg-bg-elevated text-text-muted hover:text-text-primary'
                } ${isKeywordSelected ? 'ring-2 ring-offset-1 ring-offset-bg-base' : ''}`}
                style={active ? { backgroundColor: color, ...(isKeywordSelected ? { ringColor: color } : {}) } : {}}
              >
                {skill}
              </button>
            )
          })}
        </div>
        <p className="mt-2 text-xs text-text-subtle">
          클릭하여 차트 필터링 + 키워드 빈도 확인
        </p>
      </div>

      {/* Keyword bar chart for selected skill */}
      {selectedSkillForKeywords && (
        <div className="mb-6 rounded-xl border border-border-default bg-bg-surface p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold">
              <span className="text-accent-blue">{selectedSkillForKeywords}</span> 연관 키워드 빈도
            </h3>
            <button
              onClick={() => setSelectedSkillForKeywords(null)}
              className="text-xs text-text-muted hover:text-text-primary"
            >
              닫기
            </button>
          </div>
          {mindmapLoading && <LoadingState />}
          {!mindmapLoading && keywordBarData.length > 0 && (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={keywordBarData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                <CartesianGrid {...chart.gridProps} />
                <XAxis dataKey="keyword" {...chart.xAxisProps} angle={-35} textAnchor="end" height={80} />
                <YAxis {...chart.xAxisProps} />
                <Tooltip
                  contentStyle={chart.tooltipStyle}
                  formatter={(value: number | undefined) => [`${value ?? 0}건`, '공고 수']}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} animationDuration={600}>
                  {keywordBarData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
          {!mindmapLoading && keywordBarData.length === 0 && (
            <p className="py-8 text-center text-sm text-text-muted">키워드 데이터가 없습니다</p>
          )}
        </div>
      )}

      {/* Line Chart */}
      <div className="rounded-xl border border-border-default bg-bg-surface p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold">연도별 스킬 언급 추이</h3>
          <span className="text-sm text-text-muted">{data.period}</span>
        </div>
        <ResponsiveContainer width="100%" height={380}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid {...chart.gridProps} horizontal />
            <XAxis dataKey="year" {...chart.xAxisProps} />
            <YAxis {...chart.xAxisProps} />
            <Tooltip contentStyle={chart.tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 12, fontFamily: 'JetBrains Mono', color: chart.axisTick }} />
            {allSkills.filter((s) => currentActive.has(s)).map((skill, idx) => (
              <Line
                key={skill}
                type="monotone"
                dataKey={skill}
                stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 4, fill: CHART_COLORS[idx % CHART_COLORS.length] }}
                activeDot={{ r: 6 }}
                animationDuration={600}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Data table */}
      <div className="mt-6 overflow-hidden rounded-xl border border-border-default bg-bg-surface">
        <div className="border-b border-border-default bg-bg-elevated px-4 py-3">
          <h3 className="font-semibold">연도별 포스트 수 상세</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-default bg-bg-elevated text-text-muted">
              <th className="px-4 py-3 text-left font-medium">스킬</th>
              {data.yearlyData.map((row) => (
                <th key={row.year} className="px-4 py-3 text-right font-medium">{row.year}</th>
              ))}
              <th className="px-4 py-3 text-right font-medium">증감</th>
            </tr>
          </thead>
          <tbody>
            {allSkills.map((skill, idx) => {
              const color = CHART_COLORS[idx % CHART_COLORS.length]
              const counts = data.yearlyData.map((y) => y.skills.find((s) => s.skill === skill)?.postCount ?? 0)
              const first = counts[0]
              const last = counts[counts.length - 1]
              const delta = first > 0 ? Math.round(((last - first) / first) * 100) : 0
              return (
                <tr key={skill} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-2 font-mono font-medium">
                      <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                      {skill}
                    </span>
                  </td>
                  {counts.map((count, i) => (
                    <td key={i} className="px-4 py-3 text-right font-mono">{count}</td>
                  ))}
                  <td className="px-4 py-3 text-right font-mono">
                    <span className={delta >= 0 ? 'text-accent-green' : 'text-accent-red'}>
                      {delta >= 0 ? '+' : ''}{delta}%
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Recent Blog Posts */}
      {postsData && postsData.content.length > 0 && (
        <div className="mt-6 overflow-hidden rounded-xl border border-border-default bg-bg-surface">
          <div className="border-b border-border-default bg-bg-elevated px-4 py-3">
            <h3 className="font-semibold">최근 블로그 포스트</h3>
          </div>
          <div className="divide-y divide-border-muted">
            {postsData.content.map((post) => (
              <div key={post.id} className="group flex items-start gap-4 px-4 py-3 transition-colors hover:bg-bg-elevated">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <a
                      href={post.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-text-primary hover:text-accent-blue hover:underline"
                    >
                      {post.title}
                    </a>
                    <ExternalLink className="h-3.5 w-3.5 shrink-0 text-accent-blue opacity-60 transition-opacity group-hover:opacity-100" />
                  </div>
                  {post.summary && (
                    <p className="mt-1 line-clamp-2 text-sm text-text-muted">{post.summary}</p>
                  )}
                  <div className="mt-1.5 flex items-center gap-3 text-xs text-text-subtle">
                    <span>{post.companyName}</span>
                    {post.publishedAt && (
                      <span>{new Date(post.publishedAt).toLocaleDateString('ko-KR')}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
