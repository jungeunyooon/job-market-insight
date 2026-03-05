import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Label, ZAxis,
} from 'recharts'
import { Triangle } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { getThreeAxisAnalysis } from '@/api/endpoints'
import type { ThreeAxisClassification, ThreeAxisItem } from '@/api/types'

const CLASS_COLORS: Record<ThreeAxisClassification, string> = {
  ADOPTED: '#22c55e',
  OVERHYPED: '#f97316',
  ESTABLISHED: '#3b82f6',
  EMERGING: '#a855f7',
  PRACTICAL: '#06b6d4',
  HYPE_ONLY: '#ef4444',
  BLOG_DRIVEN: '#eab308',
}

const CLASS_LABELS: Record<ThreeAxisClassification, string> = {
  ADOPTED: '실전채택',
  OVERHYPED: '과대포장',
  ESTABLISHED: '안정기술',
  EMERGING: '태동기',
  PRACTICAL: '실무핵심',
  HYPE_ONLY: '과대광고',
  BLOG_DRIVEN: '블로그주도',
}

const CLASS_DESC: Record<ThreeAxisClassification, string> = {
  ADOPTED: 'Buzz HIGH + Job HIGH',
  OVERHYPED: 'Buzz HIGH + Job LOW + Blog HIGH',
  ESTABLISHED: 'Buzz LOW + Job HIGH',
  EMERGING: '모두 LOW',
  PRACTICAL: 'Buzz LOW + Job HIGH + Blog HIGH',
  HYPE_ONLY: 'Buzz HIGH + Job LOW + Blog LOW',
  BLOG_DRIVEN: 'Buzz LOW + Job LOW + Blog HIGH',
}

interface ScatterItem {
  skill: string
  trendScore: number
  jobScore: number
  blogSize: number
  classification: ThreeAxisClassification
  insight: string
  raw: ThreeAxisItem
}

function normalizeToScatter(items: ThreeAxisItem[]): ScatterItem[] {
  const maxTrend = Math.max(...items.map(i => i.trendMentions), 1)
  const maxJob = Math.max(...items.map(i => i.jobPercentage), 1)
  const maxBlog = Math.max(...items.map(i => i.blogMentions), 1)
  return items.map(i => ({
    skill: i.skill,
    trendScore: Math.round((i.trendMentions / maxTrend) * 100),
    jobScore: Math.round((i.jobPercentage / maxJob) * 100),
    blogSize: Math.max(Math.round((i.blogMentions / maxBlog) * 200) + 40, 50),
    classification: i.classification,
    insight: i.insight,
    raw: i,
  }))
}

interface CustomDotProps {
  cx?: number
  cy?: number
  payload?: ScatterItem
}

function CustomDot({ cx = 0, cy = 0, payload }: CustomDotProps) {
  if (!payload) return null
  const color = CLASS_COLORS[payload.classification]
  const r = Math.max(Math.sqrt(payload.blogSize) * 0.7, 5)
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={color} fillOpacity={0.7} stroke={color} strokeWidth={1.5} />
      <text x={cx + r + 4} y={cy + 4} fontSize={11} fontFamily="JetBrains Mono" fill={color} style={{ pointerEvents: 'none' }}>
        {payload.skill}
      </text>
    </g>
  )
}

interface TooltipEntry { payload: ScatterItem }
interface CustomTooltipProps { active?: boolean; payload?: TooltipEntry[] }

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  const chart = useChartStyles()
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const r = d.raw
  return (
    <div style={{ ...chart.tooltipStyle, padding: '12px 16px', minWidth: 220 }}>
      <p className="mb-1.5 font-mono text-sm font-bold" style={{ color: CLASS_COLORS[d.classification] }}>{d.skill}</p>
      <div className="space-y-0.5 text-xs" style={{ color: chart.tooltipText }}>
        <p>분류: <span className="font-semibold">{CLASS_LABELS[d.classification]}</span></p>
        <p>트렌드 언급: <span className="font-mono">{r.trendMentions}</span> (#{r.trendRank || '-'})</p>
        <p>채용 공고: <span className="font-mono">{r.jobPostings}</span> ({r.jobPercentage}%)</p>
        <p>블로그 언급: <span className="font-mono">{r.blogMentions}</span> ({r.blogPercentage}%)</p>
      </div>
      {d.insight && <p className="mt-2 text-xs" style={{ color: chart.axisTick }}>{d.insight}</p>}
    </div>
  )
}

export function ThreeAxisAnalysis() {
  const chart = useChartStyles()
  const [filter, setFilter] = useState<ThreeAxisClassification | 'ALL'>('ALL')
  const [days, setDays] = useState(30)

  const { data, loading, error, refetch } = useApi(
    () => getThreeAxisAnalysis({ topN: 25, days }),
    [days],
  )

  if (loading) return <LoadingState />
  if (error || !data) return <ErrorState message={error || '데이터를 불러올 수 없습니다'} onRetry={refetch} />

  const scatterData = normalizeToScatter(data.items)
  const filtered = filter === 'ALL' ? scatterData : scatterData.filter(d => d.classification === filter)

  // Count by classification
  const counts = data.items.reduce((acc, i) => {
    acc[i.classification] = (acc[i.classification] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const refLineStyle = { stroke: chart.gridStroke, strokeDasharray: '4 4', strokeWidth: 1.5 }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">3축 분석</h2>
        <p className="mt-1 text-sm text-text-muted">
          커뮤니티 관심(X) × 채용 수요(Y) × 블로그 실무(버블 크기) — 7가지 분류
        </p>
      </div>

      {/* KPI */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <KpiCard label="분석 스킬" value={data.items.length} icon={<Triangle className="h-5 w-5" />} />
        <KpiCard label="트렌드 포스트" value={data.totalTrendPosts.toLocaleString()} />
        <KpiCard label="채용 공고" value={data.totalJobPostings.toLocaleString()} />
        <KpiCard label="블로그 포스트" value={data.totalBlogPosts.toLocaleString()} />
      </div>

      {/* Period selector */}
      <div className="mb-4 flex items-center gap-3">
        <span className="text-sm text-text-muted">기간:</span>
        {[7, 14, 30, 60, 90].map(d => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`cursor-pointer rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              days === d ? 'bg-accent-blue text-white' : 'bg-bg-surface text-text-muted hover:bg-bg-elevated'
            }`}
          >
            {d}일
          </button>
        ))}
      </div>

      {/* Classification filter */}
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setFilter('ALL')}
          className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            filter === 'ALL' ? 'bg-accent-blue text-white' : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
          }`}
        >
          전체 ({data.items.length})
        </button>
        {(Object.keys(CLASS_LABELS) as ThreeAxisClassification[]).map(cls => {
          const count = counts[cls] || 0
          if (count === 0) return null
          return (
            <button
              key={cls}
              onClick={() => setFilter(cls)}
              className={`flex cursor-pointer items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                filter === cls ? 'ring-2 ring-offset-1' : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
              }`}
              style={filter === cls ? { backgroundColor: CLASS_COLORS[cls] + '22', color: CLASS_COLORS[cls] } : {}}
            >
              <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CLASS_COLORS[cls] }} />
              {CLASS_LABELS[cls]} ({count})
            </button>
          )
        })}
      </div>

      {/* Scatter Chart */}
      <div className="rounded-xl border border-border-default bg-bg-surface p-6">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 20, right: 140, bottom: 40, left: 20 }}>
            <CartesianGrid {...chart.gridProps} horizontal />
            <XAxis type="number" dataKey="trendScore" domain={[0, 100]} {...chart.xAxisProps}>
              <Label value="트렌드 Buzz 점수" position="insideBottom" offset={-20} style={{ fill: chart.axisTick, fontSize: 12 }} />
            </XAxis>
            <YAxis type="number" dataKey="jobScore" domain={[0, 100]} {...chart.xAxisProps}>
              <Label value="채용 수요 점수" angle={-90} position="insideLeft" offset={10} style={{ fill: chart.axisTick, fontSize: 12 }} />
            </YAxis>
            <ZAxis type="number" dataKey="blogSize" range={[40, 400]} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine x={30} {...refLineStyle} />
            <ReferenceLine y={30} {...refLineStyle} />
            <Scatter data={filtered} shape={(props: CustomDotProps) => <CustomDot {...props} />} />
          </ScatterChart>
        </ResponsiveContainer>
        <p className="mt-2 text-center text-xs text-text-subtle">
          버블 크기 = 블로그 언급량 (클수록 실무에서 많이 다룸)
        </p>
      </div>

      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-7">
        {(Object.keys(CLASS_LABELS) as ThreeAxisClassification[]).map(cls => (
          <div key={cls} className="flex items-start gap-2 rounded-lg border border-border-muted bg-bg-surface p-3">
            <span className="mt-0.5 inline-block h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: CLASS_COLORS[cls] }} />
            <div>
              <p className="text-xs font-semibold" style={{ color: CLASS_COLORS[cls] }}>{CLASS_LABELS[cls]}</p>
              <p className="text-[10px] text-text-subtle">{CLASS_DESC[cls]}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Detail Table */}
      <div className="mt-6 overflow-hidden rounded-xl border border-border-default bg-bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-default bg-bg-elevated text-text-muted">
              <th className="px-4 py-3 text-left font-medium">스킬</th>
              <th className="px-4 py-3 text-right font-medium">트렌드</th>
              <th className="px-4 py-3 text-right font-medium">채용</th>
              <th className="px-4 py-3 text-right font-medium">채용%</th>
              <th className="px-4 py-3 text-right font-medium">블로그</th>
              <th className="px-4 py-3 text-right font-medium">블로그%</th>
              <th className="px-4 py-3 text-center font-medium">분류</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map(item => (
              <tr key={item.skill} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                <td className="px-4 py-3 font-mono font-medium">{item.skill}</td>
                <td className="px-4 py-3 text-right font-mono">{item.trendMentions}</td>
                <td className="px-4 py-3 text-right font-mono">{item.jobPostings}</td>
                <td className="px-4 py-3 text-right font-mono">{item.jobPercentage}%</td>
                <td className="px-4 py-3 text-right font-mono">{item.blogMentions}</td>
                <td className="px-4 py-3 text-right font-mono">{item.blogPercentage}%</td>
                <td className="px-4 py-3 text-center">
                  <span
                    className="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold"
                    style={{ backgroundColor: CLASS_COLORS[item.classification] + '22', color: CLASS_COLORS[item.classification] }}
                  >
                    {CLASS_LABELS[item.classification]}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}
