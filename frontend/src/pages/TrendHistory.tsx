import { useState, useMemo, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'
import { History } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { LoadingState } from '@/components/ui/LoadingState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { getSnapshotHistory, getTrendRanking } from '@/api/endpoints'
import type { TrendSource, SnapshotPoint, SnapshotHistoryResponse } from '@/api/types'

const SOURCES: { value: TrendSource; label: string }[] = [
  { value: 'GEEKNEWS', label: 'GeekNews' },
  { value: 'HN', label: 'HackerNews' },
  { value: 'DEVTO', label: 'dev.to' },
]

const CHART_COLORS = ['#2f81f7', '#3fb950', '#d29922', '#f85149', '#a371f7', '#39c5cf', '#f28e2b', '#e15759']

function formatDate(iso: string): string {
  const d = new Date(iso)
  return `${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`
}

export function TrendHistory() {
  const chart = useChartStyles()
  const [source, setSource] = useState<TrendSource>('GEEKNEWS')
  const [days, setDays] = useState(30)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [historyMap, setHistoryMap] = useState<Record<string, SnapshotHistoryResponse>>({})

  // Get top skills for the source to populate selection
  const { data: rankingData, loading: rankLoading } = useApi(
    () => getTrendRanking({ source, days, topN: 10 }),
    [source, days],
  )

  // Available skills from ranking
  const availableSkills = useMemo(
    () => rankingData?.rankings.map(r => r.skill) || [],
    [rankingData],
  )

  // Auto-select top 3 skills when ranking data loads
  useEffect(() => {
    if (availableSkills.length > 0 && selectedSkills.length === 0) {
      setSelectedSkills(availableSkills.slice(0, 3))
    }
  }, [availableSkills]) // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch history for all selected skills via Promise.all (no hooks in loops)
  const fetchHistories = useCallback(() => {
    if (selectedSkills.length === 0) {
      setHistoryMap({})
      return
    }
    Promise.all(
      selectedSkills.map(skill =>
        getSnapshotHistory({ source, skill, days }).then(data => ({ skill, data })),
      ),
    ).then(results => {
      const map: Record<string, SnapshotHistoryResponse> = {}
      for (const { skill, data } of results) map[skill] = data
      setHistoryMap(map)
    }).catch(() => setHistoryMap({}))
  }, [selectedSkills, source, days])

  useEffect(() => { fetchHistories() }, [fetchHistories])

  // Merge history data into chart-friendly format
  const chartData = useMemo(() => {
    const timeMap = new Map<string, Record<string, string | number>>()

    for (const [skill, data] of Object.entries(historyMap)) {
      if (!data?.history) continue
      for (const point of data.history) {
        const key = formatDate(point.snapshotAt)
        if (!timeMap.has(key)) timeMap.set(key, { date: key })
        const row = timeMap.get(key)!
        row[skill] = point.rank
      }
    }

    return Array.from(timeMap.values()).sort((a, b) =>
      String(a.date).localeCompare(String(b.date)),
    )
  }, [historyMap])

  // Latest snapshot for KPI
  const latestPoints: Record<string, SnapshotPoint> = {}
  for (const [skill, data] of Object.entries(historyMap)) {
    if (data?.history?.length) {
      latestPoints[skill] = data.history[data.history.length - 1]
    }
  }

  const toggleSkill = (skill: string) => {
    setSelectedSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill],
    )
  }

  if (rankLoading) return <LoadingState />

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">트렌드 히스토리</h2>
        <p className="mt-1 text-sm text-text-muted">
          스킬별 트렌드 순위 변화를 시계열로 추적합니다
        </p>
      </div>

      {/* KPI */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <KpiCard label="데이터 소스" value={SOURCES.find(s => s.value === source)?.label || source} icon={<History className="h-5 w-5" />} />
        <KpiCard label="조회 기간" value={`${days}일`} />
        <KpiCard label="추적 스킬" value={selectedSkills.length} />
        <KpiCard label="스냅샷 수" value={chartData.length} />
      </div>

      {/* Controls */}
      <div className="mb-4 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-text-muted">소스:</span>
          {SOURCES.map(s => (
            <button
              key={s.value}
              onClick={() => { setSource(s.value); setSelectedSkills([]) }}
              className={`cursor-pointer rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                source === s.value ? 'bg-accent-blue text-white' : 'bg-bg-surface text-text-muted hover:bg-bg-elevated'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
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
      </div>

      {/* Skill selector */}
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <span className="text-sm text-text-muted">스킬:</span>
        {availableSkills.map((skill, i) => {
          const active = selectedSkills.includes(skill)
          const color = CHART_COLORS[i % CHART_COLORS.length]
          return (
            <button
              key={skill}
              onClick={() => toggleSkill(skill)}
              className={`cursor-pointer rounded-md border px-3 py-1.5 font-mono text-xs font-medium transition-colors ${
                active ? 'border-transparent text-white' : 'border-border-default bg-bg-surface text-text-muted hover:bg-bg-elevated'
              }`}
              style={active ? { backgroundColor: color } : {}}
            >
              {skill}
            </button>
          )
        })}
      </div>

      {/* Line Chart */}
      {chartData.length > 0 ? (
        <div className="rounded-xl border border-border-default bg-bg-surface p-6">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 10, right: 30, bottom: 20, left: 10 }}>
              <CartesianGrid {...chart.gridProps} horizontal />
              <XAxis dataKey="date" {...chart.xAxisProps} />
              <YAxis
                reversed
                domain={[1, 'auto']}
                allowDecimals={false}
                {...chart.xAxisProps}
                label={{ value: '순위 (낮을수록 높음)', angle: -90, position: 'insideLeft', offset: 10, style: { fill: chart.axisTick, fontSize: 12 } }}
              />
              <Tooltip
                contentStyle={chart.tooltipStyle}
                labelFormatter={(label) => `날짜: ${label}`}
                formatter={(value) => [`#${value}`, '']}
              />
              <Legend />
              {selectedSkills.map((skill) => (
                <Line
                  key={skill}
                  type="monotone"
                  dataKey={skill}
                  stroke={CHART_COLORS[availableSkills.indexOf(skill) % CHART_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <p className="mt-2 text-center text-xs text-text-subtle">
            Y축이 반전되어 있습니다 — 위로 갈수록 높은 순위
          </p>
        </div>
      ) : (
        <div className="flex h-64 items-center justify-center rounded-xl border border-border-default bg-bg-surface">
          <p className="text-sm text-text-muted">
            {selectedSkills.length === 0 ? '추적할 스킬을 선택해주세요' : '스냅샷 데이터가 없습니다. 동기화 실행 후 다시 확인하세요.'}
          </p>
        </div>
      )}

      {/* Current rankings table */}
      {Object.keys(latestPoints).length > 0 && (
        <div className="mt-6 overflow-hidden rounded-xl border border-border-default bg-bg-surface">
          <div className="border-b border-border-default bg-bg-elevated px-4 py-3">
            <h3 className="text-sm font-semibold">최신 스냅샷 현황</h3>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border-default text-text-muted">
                <th className="px-4 py-3 text-left font-medium">스킬</th>
                <th className="px-4 py-3 text-right font-medium">현재 순위</th>
                <th className="px-4 py-3 text-right font-medium">언급 수</th>
                <th className="px-4 py-3 text-right font-medium">스냅샷 시각</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(latestPoints)
                .sort(([, a], [, b]) => a.rank - b.rank)
                .map(([skill, point]) => (
                  <tr key={skill} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                    <td className="px-4 py-3 font-mono font-medium">{skill}</td>
                    <td className="px-4 py-3 text-right font-mono">#{point.rank}</td>
                    <td className="px-4 py-3 text-right font-mono">{point.mentionCount}</td>
                    <td className="px-4 py-3 text-right text-text-muted">{formatDate(point.snapshotAt)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}
