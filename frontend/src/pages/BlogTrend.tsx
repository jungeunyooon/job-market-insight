import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'
import { BookOpen } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { useChartStyles } from '@/hooks/useChartStyles'
import { BLOG_TRENDS, BLOG_TREND_COMPANIES, type BlogTrendItem } from '@/data/demo'

const CHART_COLORS = [
  '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948',
]

// Derive the list of all skills from the data
const ALL_SKILLS = Array.from(
  new Set(BLOG_TRENDS.flatMap((row) => Object.keys(row.skills)))
)

// Build flat chart data for Recharts: [{ year: 2022, Kubernetes: 45, ... }, ...]
function buildChartData(items: BlogTrendItem[], activeSkills: Set<string>) {
  return items.map((row) => {
    const point: Record<string, number | string> = { year: String(row.year) }
    for (const skill of activeSkills) {
      point[skill] = row.skills[skill] ?? 0
    }
    return point
  })
}

export function BlogTrend() {
  const chart = useChartStyles()
  const [activeSkills, setActiveSkills] = useState<Set<string>>(new Set(ALL_SKILLS))

  const chartData = buildChartData(BLOG_TRENDS, activeSkills)

  const totalPosts = BLOG_TRENDS.reduce((sum, row) => {
    return sum + Object.values(row.skills).reduce((a, b) => a + b, 0)
  }, 0)
  const companiesCount = BLOG_TREND_COMPANIES.length
  const yearsCount = BLOG_TRENDS.length

  function toggleSkill(skill: string) {
    setActiveSkills((prev) => {
      const next = new Set(prev)
      if (next.has(skill)) {
        // Keep at least one skill active
        if (next.size > 1) next.delete(skill)
      } else {
        next.add(skill)
      }
      return next
    })
  }

  function toggleAll() {
    if (activeSkills.size === ALL_SKILLS.length) {
      setActiveSkills(new Set([ALL_SKILLS[0]]))
    } else {
      setActiveSkills(new Set(ALL_SKILLS))
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">블로그 트렌드</h2>
        <p className="mt-1 text-sm text-text-muted">
          기술 블로그 연도별 스킬 언급 추이 (2022–2025)
        </p>
      </div>

      {/* KPI Cards */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <KpiCard
          label="총 블로그 포스트"
          value={totalPosts.toLocaleString()}
          icon={<BookOpen className="h-5 w-5" />}
        />
        <KpiCard label="분석 기업 수" value={companiesCount} />
        <KpiCard label="분석 연도" value={`${yearsCount}년`} />
      </div>

      {/* Skill filter checkboxes */}
      <div className="mb-6 rounded-xl border border-border-default bg-bg-surface px-5 py-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm font-medium text-text-primary">스킬 필터</span>
          <button
            onClick={toggleAll}
            className="text-xs text-accent-blue hover:underline"
          >
            {activeSkills.size === ALL_SKILLS.length ? '전체 해제' : '전체 선택'}
          </button>
        </div>
        <div className="flex flex-wrap gap-3">
          {ALL_SKILLS.map((skill, idx) => {
            const color = CHART_COLORS[idx % CHART_COLORS.length]
            const checked = activeSkills.has(skill)
            return (
              <label
                key={skill}
                className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-1.5 text-sm transition-colors hover:bg-bg-elevated"
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleSkill(skill)}
                  className="hidden"
                />
                <span
                  className="inline-block h-3 w-3 rounded-sm transition-opacity"
                  style={{
                    backgroundColor: color,
                    opacity: checked ? 1 : 0.25,
                  }}
                />
                <span
                  className="font-mono"
                  style={{ color: checked ? color : undefined }}
                >
                  {skill}
                </span>
              </label>
            )
          })}
        </div>
      </div>

      {/* Line Chart */}
      <div className="rounded-xl border border-border-default bg-bg-surface p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold">연도별 스킬 언급 추이</h3>
          <span className="text-sm text-text-muted">포스트 수 기준</span>
        </div>
        <ResponsiveContainer width="100%" height={380}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid {...chart.gridProps} horizontal />
            <XAxis dataKey="year" {...chart.xAxisProps} />
            <YAxis {...chart.xAxisProps} />
            <Tooltip contentStyle={chart.tooltipStyle} />
            <Legend
              wrapperStyle={{ fontSize: 12, fontFamily: 'JetBrains Mono', color: chart.axisTick }}
            />
            {ALL_SKILLS.filter((s) => activeSkills.has(s)).map((skill, idx) => (
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
              {BLOG_TRENDS.map((row) => (
                <th key={row.year} className="px-4 py-3 text-right font-medium">
                  {row.year}
                </th>
              ))}
              <th className="px-4 py-3 text-right font-medium">증감</th>
            </tr>
          </thead>
          <tbody>
            {ALL_SKILLS.map((skill, idx) => {
              const color = CHART_COLORS[idx % CHART_COLORS.length]
              const first = BLOG_TRENDS[0].skills[skill] ?? 0
              const last  = BLOG_TRENDS[BLOG_TRENDS.length - 1].skills[skill] ?? 0
              const delta = first > 0 ? Math.round(((last - first) / first) * 100) : 0
              return (
                <tr key={skill} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-2 font-mono font-medium">
                      <span
                        className="inline-block h-2.5 w-2.5 rounded-full"
                        style={{ backgroundColor: color }}
                      />
                      {skill}
                    </span>
                  </td>
                  {BLOG_TRENDS.map((row) => (
                    <td key={row.year} className="px-4 py-3 text-right font-mono">
                      {row.skills[skill] ?? 0}
                    </td>
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

      {/* Companies analyzed */}
      <div className="mt-6 rounded-xl border border-border-default bg-bg-surface px-5 py-4">
        <h3 className="mb-3 text-sm font-semibold text-text-muted">분석 대상 기업</h3>
        <div className="flex flex-wrap gap-2">
          {BLOG_TREND_COMPANIES.map((company) => (
            <span
              key={company}
              className="rounded-full bg-bg-elevated px-3 py-1 text-sm font-medium text-text-primary"
            >
              {company}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
