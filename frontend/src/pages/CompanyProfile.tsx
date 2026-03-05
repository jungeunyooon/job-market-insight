import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { Building2 } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { Badge } from '@/components/ui/Badge'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useChartStyles } from '@/hooks/useChartStyles'
import { useApi } from '@/hooks/useApi'
import { getCompanyProfileByName } from '@/api/endpoints'
import { CATEGORY_LABELS, POSITION_LABELS } from '@/api/types'

const KNOWN_COMPANIES = [
  { key: '네이버', label: '네이버' },
  { key: '쿠팡', label: '쿠팡' },
  { key: '카카오', label: '카카오' },
  { key: '비바리퍼블리카', label: '토스' },
  { key: '우아한형제들', label: '배달의민족' },
  { key: '당근마켓', label: '당근' },
]

const PIE_COLORS = ['#4e79a7', '#f28e2b', '#76b7b2', '#e15759', '#59a14f']

export function CompanyProfile() {
  const [selectedCompanyName, setSelectedCompanyName] = useState(KNOWN_COMPANIES[0].key)
  const chart = useChartStyles()

  const { data: company, loading, error, refetch } = useApi(
    () => getCompanyProfileByName(selectedCompanyName),
    [selectedCompanyName],
  )

  if (loading) return <LoadingState />
  if (error || !company) return <ErrorState message={error || '데이터를 불러올 수 없습니다'} onRetry={refetch} />

  const hasData = company.totalPostings > 0 && company.topSkills.length > 0

  const pieData = Object.entries(company.positionBreakdown).map(([key, value]) => ({
    name: POSITION_LABELS[key] || key,
    value,
  }))

  const chartData = [...company.topSkills].reverse()

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">회사 기술 프로필</h2>
        <p className="mt-1 text-sm text-text-muted">
          회사별 채용공고에서 사용하는 기술 스택 분석
        </p>
      </div>

      {/* Company selector */}
      <div className="mb-6 flex flex-wrap gap-2">
        {KNOWN_COMPANIES.map((c) => (
          <button
            key={c.key}
            onClick={() => setSelectedCompanyName(c.key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              selectedCompanyName === c.key
                ? 'bg-accent-blue text-white'
                : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* KPI Cards */}
      <div className="mb-6 grid grid-cols-4 gap-4">
        <KpiCard label="회사명" value={company.companyName} icon={<Building2 className="h-5 w-5" />} />
        <KpiCard label="카테고리" value={CATEGORY_LABELS[company.category] || company.category} />
        <KpiCard label="총 공고 수" value={company.totalPostings} />
        <KpiCard label="Top 스킬" value={company.topSkills[0]?.skill || '-'} />
      </div>

      {!hasData && (
        <div className="rounded-xl border border-border-default bg-bg-surface p-10 text-center">
          <Building2 className="mx-auto mb-3 h-10 w-10 text-text-subtle" />
          <h3 className="text-lg font-semibold text-text-primary">아직 수집된 공고 데이터가 없습니다</h3>
          <p className="mt-2 text-sm text-text-muted">
            {KNOWN_COMPANIES.find(c => c.key === selectedCompanyName)?.label || selectedCompanyName}의
            채용공고를 크롤링하면 기술 스택 분석이 표시됩니다.
          </p>
          <p className="mt-1 text-xs text-text-subtle">
            배치 크롤러(<code className="rounded bg-bg-elevated px-1.5 py-0.5 font-mono">python main.py</code>)를 실행하여 데이터를 수집해 주세요.
          </p>
        </div>
      )}

      {hasData && (
        <div className="grid grid-cols-3 gap-6">
          {/* Tech Stack Chart */}
          <div className="col-span-2 rounded-xl border border-border-default bg-bg-surface p-6">
            <h3 className="mb-4 text-lg font-semibold">{company.companyName} 기술 스택</h3>
            <ResponsiveContainer width="100%" height={Math.max(300, company.topSkills.length * 45)}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 30, top: 5, bottom: 5 }}>
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
                <Bar dataKey="percentage" fill="#3fb950" radius={[0, 6, 6, 0]} animationDuration={800} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Position Breakdown Pie */}
          <div className="rounded-xl border border-border-default bg-bg-surface p-6">
            <h3 className="mb-4 text-lg font-semibold">포지션 분포</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  animationDuration={800}
                >
                  {pieData.map((_, idx) => (
                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={chart.tooltipStyle} />
                <Legend
                  formatter={(value: string) => <span style={{ color: chart.axisLabel, fontSize: 13 }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Breakdown list */}
            <div className="mt-4 space-y-2">
              {Object.entries(company.positionBreakdown).map(([pos, count]) => (
                <div key={pos} className="flex items-center justify-between text-sm">
                  <Badge>{POSITION_LABELS[pos] || pos}</Badge>
                  <span className="font-mono text-text-muted">{count}건</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}
