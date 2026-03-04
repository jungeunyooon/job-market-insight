import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Label,
} from 'recharts'
import { Zap } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { getBuzzVsHiring } from '@/api/endpoints'
import type { Classification, BuzzHiringGap } from '@/api/types'

const QUADRANT_COLORS: Record<Classification, string> = {
  OVERHYPED: '#f97316',
  ADOPTED: '#22c55e',
  ESTABLISHED: '#3b82f6',
  EMERGING: '#a855f7',
}

const QUADRANT_LABELS: Record<Classification, string> = {
  OVERHYPED: '과대포장',
  ADOPTED: '실전채택',
  ESTABLISHED: '안정기술',
  EMERGING: '떠오르는',
}

interface ScatterItem {
  skill: string
  trendScore: number
  jobScore: number
  classification: Classification
  insight: string
}

function normalizeToScatter(gaps: BuzzHiringGap[]): ScatterItem[] {
  const maxTrend = Math.max(...gaps.map((g) => g.trendMentions), 1)
  const maxJob = Math.max(...gaps.map((g) => g.jobPercentage), 1)
  return gaps.map((g) => ({
    skill: g.skill,
    trendScore: Math.round((g.trendMentions / maxTrend) * 100),
    jobScore: Math.round((g.jobPercentage / maxJob) * 100),
    classification: g.classification,
    insight: g.insight,
  }))
}

interface CustomDotProps {
  cx?: number
  cy?: number
  payload?: ScatterItem
}

function CustomDot({ cx = 0, cy = 0, payload }: CustomDotProps) {
  if (!payload) return null
  const color = QUADRANT_COLORS[payload.classification]
  return (
    <g>
      <circle cx={cx} cy={cy} r={7} fill={color} fillOpacity={0.85} stroke={color} strokeWidth={1.5} />
      <text x={cx + 10} y={cy + 4} fontSize={11} fontFamily="JetBrains Mono" fill={color} style={{ pointerEvents: 'none' }}>
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
  return (
    <div style={{ ...chart.tooltipStyle, padding: '10px 14px', minWidth: 180 }}>
      <p className="mb-1 font-mono font-bold" style={{ color: QUADRANT_COLORS[d.classification] }}>{d.skill}</p>
      <p className="text-xs" style={{ color: chart.tooltipText }}>분류: {QUADRANT_LABELS[d.classification]}</p>
      <p className="text-xs" style={{ color: chart.tooltipText }}>트렌드 점수: {d.trendScore}</p>
      <p className="text-xs" style={{ color: chart.tooltipText }}>채용 점수: {d.jobScore}</p>
      {d.insight && <p className="mt-1 text-xs" style={{ color: chart.axisTick }}>{d.insight}</p>}
    </div>
  )
}

export function BuzzVsHiring() {
  const chart = useChartStyles()
  const [filter, setFilter] = useState<Classification | 'ALL'>('ALL')

  const { data, loading, error, refetch } = useApi(
    () => getBuzzVsHiring({ topN: 20 }),
    [],
  )

  if (loading) return <LoadingState />
  if (error || !data) return <ErrorState message={error || '데이터를 불러올 수 없습니다'} onRetry={refetch} />

  const scatterData = normalizeToScatter(data.gaps)
  const filtered = filter === 'ALL' ? scatterData : scatterData.filter((d) => d.classification === filter)

  const overhypedCount = data.gaps.filter((d) => d.classification === 'OVERHYPED').length
  const adoptedCount = data.gaps.filter((d) => d.classification === 'ADOPTED').length
  const totalCount = data.gaps.length

  const refLineStyle = { stroke: chart.gridStroke, strokeDasharray: '4 4', strokeWidth: 1.5 }
  const X_THRESHOLD = 30
  const Y_THRESHOLD = 30

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">Buzz vs 채용</h2>
        <p className="mt-1 text-sm text-text-muted">
          트렌드 버즈 점수(X) vs 실제 채용공고 점수(Y) 사분면 분석
        </p>
      </div>

      <div className="mb-6 grid grid-cols-3 gap-4">
        <KpiCard label="분석 스킬 수" value={totalCount} icon={<Zap className="h-5 w-5" />} />
        <KpiCard label="과대포장(OVERHYPED)" value={overhypedCount} />
        <KpiCard label="실전채택(ADOPTED)" value={adoptedCount} />
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setFilter('ALL')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            filter === 'ALL' ? 'bg-accent-blue text-white' : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
          }`}
        >
          전체
        </button>
        {(Object.keys(QUADRANT_LABELS) as Classification[]).map((q) => (
          <button
            key={q}
            onClick={() => setFilter(q)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === q ? 'ring-2 ring-offset-1' : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
            }`}
            style={filter === q ? { backgroundColor: QUADRANT_COLORS[q] + '22', color: QUADRANT_COLORS[q] } : {}}
          >
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: QUADRANT_COLORS[q] }} />
            {QUADRANT_LABELS[q]}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-border-default bg-bg-surface p-6">
        <div className="relative">
          <div className="pointer-events-none absolute inset-0 z-10">
            <div className="absolute left-[14%] top-2 text-xs font-semibold opacity-50" style={{ color: QUADRANT_COLORS.OVERHYPED }}>과대포장</div>
            <div className="absolute right-4 top-2 text-xs font-semibold opacity-50" style={{ color: QUADRANT_COLORS.ADOPTED }}>실전채택</div>
            <div className="absolute bottom-10 left-[14%] text-xs font-semibold opacity-50" style={{ color: QUADRANT_COLORS.EMERGING }}>떠오르는</div>
            <div className="absolute bottom-10 right-4 text-xs font-semibold opacity-50" style={{ color: QUADRANT_COLORS.ESTABLISHED }}>안정기술</div>
          </div>
          <ResponsiveContainer width="100%" height={460}>
            <ScatterChart margin={{ top: 20, right: 130, bottom: 40, left: 20 }}>
              <CartesianGrid {...chart.gridProps} horizontal />
              <XAxis type="number" dataKey="trendScore" domain={[0, 100]} name="트렌드 점수" {...chart.xAxisProps}>
                <Label value="트렌드 점수 (Buzz)" position="insideBottom" offset={-20} style={{ fill: chart.axisTick, fontSize: 12 }} />
              </XAxis>
              <YAxis type="number" dataKey="jobScore" domain={[0, 100]} name="채용 점수" {...chart.xAxisProps}>
                <Label value="채용 점수 (Job Demand)" angle={-90} position="insideLeft" offset={10} style={{ fill: chart.axisTick, fontSize: 12 }} />
              </YAxis>
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine x={X_THRESHOLD} {...refLineStyle} />
              <ReferenceLine y={Y_THRESHOLD} {...refLineStyle} />
              <Scatter data={filtered} shape={(props: CustomDotProps) => <CustomDot {...props} />} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6 overflow-hidden rounded-xl border border-border-default bg-bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-default bg-bg-elevated text-text-muted">
              <th className="px-4 py-3 text-left font-medium">스킬</th>
              <th className="px-4 py-3 text-right font-medium">트렌드 언급</th>
              <th className="px-4 py-3 text-right font-medium">채용 공고</th>
              <th className="px-4 py-3 text-right font-medium">채용 비율</th>
              <th className="px-4 py-3 text-center font-medium">사분면</th>
            </tr>
          </thead>
          <tbody>
            {data.gaps.map((item) => (
              <tr key={item.skill} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                <td className="px-4 py-3 font-mono font-medium">{item.skill}</td>
                <td className="px-4 py-3 text-right font-mono">{item.trendMentions.toLocaleString()}</td>
                <td className="px-4 py-3 text-right font-mono">{item.jobPostings}</td>
                <td className="px-4 py-3 text-right font-mono">{item.jobPercentage}%</td>
                <td className="px-4 py-3 text-center">
                  <span
                    className="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold"
                    style={{ backgroundColor: QUADRANT_COLORS[item.classification] + '22', color: QUADRANT_COLORS[item.classification] }}
                  >
                    {QUADRANT_LABELS[item.classification]}
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
