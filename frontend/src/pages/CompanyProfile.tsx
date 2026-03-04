import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { Building2 } from 'lucide-react'
import { KpiCard } from '@/components/ui/KpiCard'
import { Badge } from '@/components/ui/Badge'
import { useChartStyles } from '@/hooks/useChartStyles'
import { COMPANY_PROFILES, CATEGORY_LABELS, POSITION_LABELS } from '@/data/demo'

const PIE_COLORS = ['#4e79a7', '#f28e2b', '#76b7b2', '#e15759', '#59a14f']

export function CompanyProfile() {
  const [selectedIdx, setSelectedIdx] = useState(0)
  const chart = useChartStyles()
  const company = COMPANY_PROFILES[selectedIdx]

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
        {COMPANY_PROFILES.map((c, idx) => (
          <button
            key={c.companyId}
            onClick={() => setSelectedIdx(idx)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              selectedIdx === idx
                ? 'bg-accent-blue text-white'
                : 'bg-bg-surface text-text-muted hover:bg-bg-elevated hover:text-text-primary'
            }`}
          >
            {c.companyName}
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
    </motion.div>
  )
}
