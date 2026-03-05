import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from 'recharts'
import { Badge } from '@/components/ui/Badge'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { analyzeGap } from '@/api/endpoints'
import { POSITION_LABELS, type PositionType, type SkillGap, type UserSkill } from '@/api/types'

const PRIORITY_ORDER = ['CRITICAL', 'HIGH', 'CONTINUE', 'MEDIUM', 'MAINTAINED', 'LOW'] as const
const PRIORITY_COLORS: Record<string, string> = {
  CRITICAL: '#f85149',
  HIGH: '#d29922',
  MEDIUM: '#edc948',
  LOW: '#39c5cf',
  CONTINUE: '#2f81f7',
  MAINTAINED: '#3fb950',
}

const STATUS_LABELS: Record<string, string> = {
  OWNED: '보유',
  LEARNING: '학습 중',
  NOT_OWNED: '미보유',
}

// Default skills for demo/initial state
const DEFAULT_SKILLS: UserSkill[] = [
  { name: 'Java', status: 'OWNED' },
  { name: 'Spring Boot', status: 'OWNED' },
  { name: 'Docker', status: 'OWNED' },
  { name: 'MySQL', status: 'OWNED' },
  { name: 'PostgreSQL', status: 'OWNED' },
  { name: 'JPA', status: 'OWNED' },
  { name: 'Git', status: 'OWNED' },
  { name: 'AWS', status: 'LEARNING' },
  { name: 'Kubernetes', status: 'LEARNING' },
  { name: 'Linux', status: 'LEARNING' },
  { name: 'Kafka', status: 'NOT_OWNED' },
  { name: 'Redis', status: 'NOT_OWNED' },
  { name: 'Kotlin', status: 'NOT_OWNED' },
  { name: 'Elasticsearch', status: 'NOT_OWNED' },
  { name: 'MongoDB', status: 'NOT_OWNED' },
]

export function GapAnalysis() {
  const [position, setPosition] = useState<PositionType>('BACKEND')
  const [mySkills] = useState<UserSkill[]>(DEFAULT_SKILLS)
  const chart = useChartStyles()

  const { data, loading, error, refetch } = useApi(
    () => analyzeGap({ mySkills }, position),
    [position, mySkills],
  )

  const gaps = data?.gaps ?? []
  const matchPercentage = data?.matchPercentage ?? 0

  const groupedGaps = useMemo(() => {
    const groups: Record<string, SkillGap[]> = {}
    PRIORITY_ORDER.forEach((p) => {
      const items = gaps.filter((g) => g.priority === p)
      if (items.length > 0) groups[p] = items
    })
    return groups
  }, [gaps])

  if (loading) return <LoadingState />
  if (error || !data) return <ErrorState message={error || '데이터를 불러올 수 없습니다'} onRetry={refetch} />

  const radialData = [{ name: '매칭률', value: matchPercentage, fill: chart.accentBlue }]

  const barData = gaps.slice(0, 10).map((g) => ({
    ...g,
    color: PRIORITY_COLORS[g.priority] || '#888',
  }))

  if (gaps.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="mb-6">
          <h2 className="text-2xl font-bold tracking-tight">스킬 갭 분석</h2>
          <p className="mt-1 text-sm text-text-muted">
            내 기술 스택과 시장 수요를 비교하여 학습 우선순위 분석
          </p>
        </div>
        <div className="rounded-xl border border-border-default bg-bg-surface p-8 text-center">
          <p className="text-sm text-text-primary">분석할 시장 데이터가 아직 없습니다.</p>
          <p className="mt-2 text-xs text-text-muted">
            배치 데이터 동기화(`sync-all`) 실행 후 다시 확인해 주세요.
          </p>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">스킬 갭 분석</h2>
        <p className="mt-1 text-sm text-text-muted">
          내 기술 스택과 시장 수요를 비교하여 학습 우선순위 분석
        </p>
      </div>

      {/* Position selector */}
      <div className="mb-6 flex gap-2">
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

      {/* Match Ring + Bar Chart */}
      <div className="mb-6 grid grid-cols-3 gap-6">
        {/* Radial gauge */}
        <div className="rounded-xl border border-border-default bg-bg-surface p-6 flex flex-col items-center justify-center">
          <h3 className="mb-2 text-sm font-medium text-text-muted">시장 매칭률</h3>
          <div className="relative" style={{ width: 200, height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="70%"
                outerRadius="100%"
                data={radialData}
                startAngle={90}
                endAngle={-270}
              >
                <RadialBar
                  dataKey="value"
                  cornerRadius={10}
                  background={{ fill: chart.bgElevated }}
                  animationDuration={1000}
                />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-mono text-4xl font-bold">{matchPercentage}%</span>
              <span className="text-xs text-text-muted">매칭</span>
            </div>
          </div>
          <div className="mt-4 flex gap-4 text-sm">
            <div className="text-center">
              <div className="font-mono text-lg font-bold text-accent-green">
                {gaps.filter((g) => g.userStatus === 'OWNED').length}
              </div>
              <div className="text-xs text-text-muted">보유</div>
            </div>
            <div className="text-center">
              <div className="font-mono text-lg font-bold text-accent-blue">
                {gaps.filter((g) => g.userStatus === 'LEARNING').length}
              </div>
              <div className="text-xs text-text-muted">학습 중</div>
            </div>
            <div className="text-center">
              <div className="font-mono text-lg font-bold text-accent-red">
                {gaps.filter((g) => g.userStatus === 'NOT_OWNED').length}
              </div>
              <div className="text-xs text-text-muted">미보유</div>
            </div>
          </div>
        </div>

        {/* Gap bar chart */}
        <div className="col-span-2 rounded-xl border border-border-default bg-bg-surface p-6">
          <h3 className="mb-4 text-sm font-medium text-text-muted">시장 수요 vs 보유 현황 (Top 10)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={barData} layout="vertical" margin={{ left: 90, right: 30, top: 5, bottom: 5 }}>
              <CartesianGrid {...chart.gridProps} />
              <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} {...chart.xAxisProps} />
              <YAxis type="category" dataKey="skill" width={90} {...chart.yAxisProps} />
              <Tooltip contentStyle={chart.tooltipStyle} formatter={(value: number | undefined) => [`${value ?? 0}%`, '시장 수요']} />
              <Bar dataKey="marketPercentage" radius={[0, 6, 6, 0]} animationDuration={800}>
                {barData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Priority groups */}
      <div className="space-y-4">
        {Object.entries(groupedGaps).map(([priority, items]) => (
          <div key={priority} className="rounded-xl border border-border-default bg-bg-surface overflow-hidden">
            <div className="flex items-center gap-2 border-b border-border-muted px-5 py-3">
              <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: PRIORITY_COLORS[priority] }} />
              <span className="text-sm font-semibold">{priority}</span>
              <span className="text-xs text-text-muted">({items.length}개)</span>
            </div>
            <div className="divide-y divide-border-muted">
              {items.map((item) => (
                <div key={item.skill} className="flex items-center px-5 py-3 transition-colors hover:bg-bg-elevated">
                  <span className="w-32 font-mono text-sm font-medium">{item.skill}</span>
                  <Badge variant={item.userStatus === 'OWNED' ? 'maintained' : item.userStatus === 'LEARNING' ? 'continue' : 'high'}>
                    {STATUS_LABELS[item.userStatus] || item.userStatus}
                  </Badge>
                  <div className="ml-auto flex items-center gap-6 text-sm">
                    <span className="text-text-muted">#{item.marketRank}</span>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-bg-elevated">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${item.marketPercentage}%`,
                            backgroundColor: PRIORITY_COLORS[item.priority] || '#888',
                          }}
                        />
                      </div>
                      <span className="font-mono text-xs text-text-muted w-12 text-right">
                        {item.marketPercentage}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 flex flex-wrap gap-4 rounded-xl border border-border-default bg-bg-surface px-5 py-3">
        {Object.entries(PRIORITY_COLORS).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1.5 text-xs text-text-muted">
            <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
            {key}
          </div>
        ))}
      </div>
    </motion.div>
  )
}
