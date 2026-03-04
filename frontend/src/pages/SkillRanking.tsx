import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { BarChart3 } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { getSkillRanking } from '@/api/endpoints'
import { POSITION_LABELS, type PositionType } from '@/api/types'

export function SkillRanking() {
  const [position, setPosition] = useState<PositionType>('BACKEND')
  const [topN, setTopN] = useState(15)
  const chart = useChartStyles()

  const { data, loading, error, refetch } = useApi(
    () => getSkillRanking({ positionType: position, topN }),
    [position, topN],
  )

  if (loading) return <LoadingState />
  if (error || !data) return <ErrorState message={error || '데이터를 불러올 수 없습니다'} onRetry={refetch} />

  const rankings = data.rankings
  const chartData = [...rankings].reverse()

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">기술 스킬 랭킹</h2>
        <p className="mt-1 text-sm text-text-muted">
          포지션별 채용공고에서 가장 많이 요구하는 기술 스택
        </p>
      </div>

      {/* KPI Cards */}
      <div className="mb-6 grid grid-cols-4 gap-4">
        <KpiCard label="총 공고 수" value={data.totalPostings.toLocaleString()} icon={<BarChart3 className="h-5 w-5" />} />
        <KpiCard label="분석 스킬 수" value={rankings.length} />
        <KpiCard label="Top 1 스킬" value={rankings[0]?.skill || '-'} />
        <KpiCard label="스냅샷 날짜" value={data.snapshotDate} />
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center gap-4">
        <div className="flex gap-2">
          {(['BACKEND', 'FDE', 'PRODUCT'] as PositionType[]).map((pos) => (
            <button
              key={pos}
              onClick={() => setPosition(pos)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                position === pos
                  ? 'bg-accent-blue text-white'
                  : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
              }`}
            >
              {POSITION_LABELS[pos]}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 text-sm text-text-muted">
          <span>Top</span>
          <select
            value={topN}
            onChange={(e) => setTopN(Number(e.target.value))}
            className="rounded-md border border-border-default bg-bg-surface px-2 py-1 text-text-primary"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={15}>15</option>
          </select>
        </div>
      </div>

      {/* Chart */}
      <div className="rounded-xl border border-border-default bg-bg-surface p-6">
        <ResponsiveContainer width="100%" height={Math.max(400, rankings.length * 40)}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 40, top: 10, bottom: 10 }}>
            <CartesianGrid {...chart.gridProps} />
            <XAxis
              type="number"
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
              {...chart.xAxisProps}
            />
            <YAxis type="category" dataKey="skill" width={80} {...chart.yAxisProps} />
            <Tooltip
              formatter={(value: number | undefined) => [`${value ?? 0}%`, '출현율']}
              contentStyle={chart.tooltipStyle}
            />
            <Bar dataKey="percentage" radius={[0, 6, 6, 0]} animationDuration={800}>
              {chartData.map((_, idx) => (
                <Cell key={idx} fill={idx === chartData.length - 1 ? chart.accentBlue : '#4e79a7'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="mt-6 rounded-xl border border-border-default bg-bg-surface overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-default bg-bg-elevated text-text-muted">
              <th className="px-4 py-3 text-left font-medium">순위</th>
              <th className="px-4 py-3 text-left font-medium">스킬</th>
              <th className="px-4 py-3 text-right font-medium">공고 수</th>
              <th className="px-4 py-3 text-right font-medium">출현율</th>
              <th className="px-4 py-3 text-right font-medium">필수 비율</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((r) => (
              <tr key={r.skill} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                <td className="px-4 py-3 font-mono text-text-muted">#{r.rank}</td>
                <td className="px-4 py-3 font-mono font-medium">{r.skill}</td>
                <td className="px-4 py-3 text-right font-mono">{r.count}</td>
                <td className="px-4 py-3 text-right font-mono">{r.percentage}%</td>
                <td className="px-4 py-3 text-right font-mono">{(r.requiredRatio * 100).toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}
