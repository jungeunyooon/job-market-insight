import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts'
import { useChartStyles } from '@/hooks/useChartStyles'
import { SKILL_RANKINGS, POSITION_LABELS, type PositionType } from '@/data/demo'

const POSITION_COLORS: Record<string, string> = {
  BACKEND: '#4e79a7',
  FDE: '#f28e2b',
  PRODUCT: '#76b7b2',
}

export function PositionCompare() {
  const [selected, setSelected] = useState<PositionType[]>(['BACKEND', 'FDE'])
  const [viewMode, setViewMode] = useState<'bar' | 'radar'>('bar')
  const chart = useChartStyles()

  const togglePosition = (pos: PositionType) => {
    setSelected((prev) =>
      prev.includes(pos) ? prev.filter((p) => p !== pos) : [...prev, pos]
    )
  }

  // Merge all skills from selected positions
  const allSkills = new Set<string>()
  selected.forEach((pos) => {
    SKILL_RANKINGS[pos].rankings.slice(0, 10).forEach((r) => allSkills.add(r.skill))
  })

  const mergedData = Array.from(allSkills).map((skill) => {
    const row: Record<string, string | number> = { skill }
    selected.forEach((pos) => {
      const found = SKILL_RANKINGS[pos].rankings.find((r) => r.skill === skill)
      row[pos] = found?.percentage || 0
    })
    return row
  })

  // Common and unique skills
  const skillSets: Record<string, Set<string>> = {}
  selected.forEach((pos) => {
    skillSets[pos] = new Set(SKILL_RANKINGS[pos].rankings.slice(0, 10).map((r) => r.skill))
  })
  const commonSkills = selected.length >= 2
    ? [...Object.values(skillSets).reduce((a, b) => new Set([...a].filter((x) => b.has(x))))]
    : []
  const uniqueSkills: Record<string, string[]> = {}
  selected.forEach((pos) => {
    const others = new Set<string>()
    selected.filter((p) => p !== pos).forEach((p) => skillSets[p]?.forEach((s) => others.add(s)))
    uniqueSkills[pos] = [...(skillSets[pos] || [])].filter((s) => !others.has(s))
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">포지션별 기술 비교</h2>
        <p className="mt-1 text-sm text-text-muted">
          서로 다른 포지션에서 요구하는 기술 스택 비교
        </p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex gap-2">
          {(['BACKEND', 'FDE', 'PRODUCT'] as PositionType[]).map((pos) => (
            <button
              key={pos}
              onClick={() => togglePosition(pos)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                selected.includes(pos)
                  ? 'text-white'
                  : 'bg-bg-surface text-text-muted hover:bg-bg-elevated'
              }`}
              style={selected.includes(pos) ? { backgroundColor: POSITION_COLORS[pos] } : {}}
            >
              {POSITION_LABELS[pos]}
            </button>
          ))}
        </div>
        <div className="flex gap-1 rounded-lg bg-bg-surface p-1">
          <button
            onClick={() => setViewMode('bar')}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${viewMode === 'bar' ? 'bg-bg-elevated text-text-primary' : 'text-text-muted'}`}
          >
            막대
          </button>
          <button
            onClick={() => setViewMode('radar')}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${viewMode === 'radar' ? 'bg-bg-elevated text-text-primary' : 'text-text-muted'}`}
          >
            레이더
          </button>
        </div>
      </div>

      {selected.length < 2 ? (
        <div className="rounded-xl border border-border-default bg-bg-surface p-12 text-center text-text-muted">
          2개 이상의 포지션을 선택하세요
        </div>
      ) : (
        <>
          {/* Chart */}
          <div className="rounded-xl border border-border-default bg-bg-surface p-6">
            {viewMode === 'bar' ? (
              <ResponsiveContainer width="100%" height={500}>
                <BarChart data={mergedData} layout="vertical" margin={{ left: 90, right: 30, top: 10, bottom: 10 }}>
                  <CartesianGrid {...chart.gridProps} />
                  <XAxis
                    type="number"
                    domain={[0, 100]}
                    tickFormatter={(v) => `${v}%`}
                    {...chart.xAxisProps}
                  />
                  <YAxis type="category" dataKey="skill" width={90} {...chart.yAxisProps} />
                  <Tooltip
                    contentStyle={chart.tooltipStyle}
                    formatter={(value: number | undefined, name: string | undefined) => [`${value ?? 0}%`, name ? (POSITION_LABELS[name] || name) : '']}
                  />
                  <Legend formatter={(value) => POSITION_LABELS[value] || value} />
                  {selected.map((pos) => (
                    <Bar
                      key={pos}
                      dataKey={pos}
                      fill={POSITION_COLORS[pos]}
                      radius={[0, 4, 4, 0]}
                      animationDuration={800}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <ResponsiveContainer width="100%" height={500}>
                <RadarChart data={mergedData}>
                  <PolarGrid stroke={chart.axisStroke} />
                  <PolarAngleAxis
                    dataKey="skill"
                    tick={{ fill: chart.axisLabel, fontSize: 11, fontFamily: 'JetBrains Mono' }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={{ fill: chart.axisTick, fontSize: 10 }}
                  />
                  {selected.map((pos) => (
                    <Radar
                      key={pos}
                      name={POSITION_LABELS[pos]}
                      dataKey={pos}
                      stroke={POSITION_COLORS[pos]}
                      fill={POSITION_COLORS[pos]}
                      fillOpacity={0.15}
                      animationDuration={800}
                    />
                  ))}
                  <Legend formatter={(value) => value} />
                  <Tooltip contentStyle={chart.tooltipStyle} />
                </RadarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Common & Unique Skills */}
          <div className="mt-6 grid grid-cols-2 gap-6">
            <div className="rounded-xl border border-border-default bg-bg-surface p-6">
              <h3 className="mb-3 text-lg font-semibold">공통 스킬</h3>
              <div className="flex flex-wrap gap-2">
                {commonSkills.map((skill) => (
                  <span key={skill} className="rounded-md border border-accent-blue/30 bg-accent-blue/10 px-3 py-1 font-mono text-sm text-accent-blue">
                    {skill}
                  </span>
                ))}
                {commonSkills.length === 0 && <p className="text-sm text-text-muted">공통 스킬이 없습니다</p>}
              </div>
            </div>
            <div className="rounded-xl border border-border-default bg-bg-surface p-6">
              <h3 className="mb-3 text-lg font-semibold">고유 스킬</h3>
              <div className="space-y-3">
                {selected.map((pos) => (
                  <div key={pos}>
                    <span className="text-sm font-medium" style={{ color: POSITION_COLORS[pos] }}>
                      {POSITION_LABELS[pos]}
                    </span>
                    <div className="mt-1 flex flex-wrap gap-1.5">
                      {(uniqueSkills[pos] || []).map((skill) => (
                        <span key={skill} className="rounded-md border border-border-default bg-bg-elevated px-2 py-0.5 font-mono text-xs text-text-primary">
                          {skill}
                        </span>
                      ))}
                      {(uniqueSkills[pos] || []).length === 0 && (
                        <span className="text-xs text-text-subtle">없음</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </motion.div>
  )
}
