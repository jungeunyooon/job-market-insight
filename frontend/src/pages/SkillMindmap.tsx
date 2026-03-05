import { useState, useMemo, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  Treemap, ResponsiveContainer, Tooltip,
} from 'recharts'
import { Network, Hash, TrendingUp } from 'lucide-react'
import ForceGraph2D from 'react-force-graph-2d'
import { KpiCard } from '@/components/ui/KpiCard'
import { LoadingState } from '@/components/ui/LoadingState'
import { ErrorState } from '@/components/ui/ErrorState'
import { useApi } from '@/hooks/useApi'
import { getSkillRanking, getSkillMindmap } from '@/api/endpoints'
import type { SkillMindmapResponse } from '@/api/types'

const COLORS = [
  '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
  '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac',
  '#6baed6', '#fd8d3c', '#74c476', '#9e9ac8', '#e377c2',
]

const GROUP_COLORS: Record<string, string> = {
  'Language': '#4e79a7',
  'Framework': '#f28e2b',
  'Database': '#e15759',
  'DevOps': '#76b7b2',
  'Cloud': '#59a14f',
  'Tool': '#edc948',
  'Library': '#b07aa1',
}

interface TreemapNode {
  [key: string]: string | number
  name: string
  size: number
  percentage: number
  fill: string
}

function TreemapContent(props: { x: number; y: number; width: number; height: number; name: string; fill: string }) {
  const { x, y, width, height, name, fill } = props
  if (width < 40 || height < 24) return null
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} rx={4} fill={fill} stroke="var(--color-bg-base)" strokeWidth={2} />
      {width > 60 && height > 30 && (
        <text x={x + width / 2} y={y + height / 2} textAnchor="middle" dominantBaseline="central" fill="#fff" fontSize={Math.min(14, width / 8)} fontWeight={500}>
          {name}
        </text>
      )}
    </g>
  )
}

export function SkillMindmap() {
  const [selectedSkill, setSelectedSkill] = useState<string>('')
  const graphRef = useRef<InstanceType<typeof ForceGraph2D>>(null)

  const { data: rankingData, loading: rankingLoading } = useApi(
    () => getSkillRanking({ topN: 50 }),
    [],
  )

  const { data, loading, error, refetch } = useApi(
    () => selectedSkill ? getSkillMindmap(selectedSkill) : Promise.resolve(null as unknown as SkillMindmapResponse),
    [selectedSkill],
  )

  const skillOptions = useMemo(() => {
    if (!rankingData) return []
    return rankingData.rankings.map((r) => r.skill)
  }, [rankingData])

  // 첫 번째 스킬 자동 선택
  if (!selectedSkill && skillOptions.length > 0) {
    setSelectedSkill(skillOptions[0])
  }

  const treemapData: TreemapNode[] = useMemo(() => {
    if (!data?.allKeywords) return []
    return data.allKeywords.map((kw, i) => ({
      name: kw.keyword,
      size: kw.postingCount,
      percentage: kw.percentage,
      fill: COLORS[i % COLORS.length],
    }))
  }, [data])

  // Force-directed graph data
  const graphData = useMemo(() => {
    if (!data?.allKeywords || !data.skillName) return { nodes: [], links: [] }

    const centerNode = {
      id: data.skillName,
      group: 'center',
      val: 30,
      label: data.skillName,
    }

    // Determine group for each keyword
    const getGroupColor = (kw: { keyword: string }, idx: number) => {
      if (data.keywordGroups) {
        for (const [group, keywords] of Object.entries(data.keywordGroups)) {
          if (keywords.some(k => k.keyword === kw.keyword)) {
            return GROUP_COLORS[group] || COLORS[idx % COLORS.length]
          }
        }
      }
      return COLORS[idx % COLORS.length]
    }

    const getGroup = (kw: { keyword: string }) => {
      if (data.keywordGroups) {
        for (const [group, keywords] of Object.entries(data.keywordGroups)) {
          if (keywords.some(k => k.keyword === kw.keyword)) {
            return group
          }
        }
      }
      return 'Other'
    }

    const keywordNodes = data.allKeywords.map((kw, i) => ({
      id: kw.keyword,
      group: getGroup(kw),
      val: Math.max(4, Math.sqrt(kw.postingCount) * 3),
      label: `${kw.keyword} (${kw.postingCount}건, ${kw.percentage.toFixed(1)}%)`,
      color: getGroupColor(kw, i),
      count: kw.postingCount,
    }))

    const links = data.allKeywords.map((kw) => ({
      source: data.skillName,
      target: kw.keyword,
    }))

    return {
      nodes: [centerNode, ...keywordNodes],
      links,
    }
  }, [data])

  const nodeCanvasObject = useCallback((node: Record<string, unknown>, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.id as string
    const val = (node.val as number) || 5
    const radius = Math.sqrt(val) * 2
    const isCenter = (node.group as string) === 'center'
    const fontSize = isCenter ? 14 / globalScale : Math.max(10 / globalScale, 3)

    // Draw circle
    ctx.beginPath()
    ctx.arc(node.x as number, node.y as number, radius, 0, 2 * Math.PI)
    ctx.fillStyle = isCenter ? '#2f81f7' : (node.color as string) || '#8b949e'
    ctx.fill()

    if (isCenter) {
      ctx.strokeStyle = '#58a6ff'
      ctx.lineWidth = 2 / globalScale
      ctx.stroke()
    }

    // Draw label
    if (globalScale > 0.6 || isCenter) {
      ctx.font = `${isCenter ? 'bold ' : ''}${fontSize}px JetBrains Mono, monospace`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillStyle = '#e6edf3'
      ctx.fillText(label, node.x as number, (node.y as number) + radius + fontSize + 1)
    }
  }, [])

  if (rankingLoading) return <LoadingState />

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">스킬 마인드맵</h2>
        <p className="mt-1 text-sm text-text-muted">
          각 스킬이 채용공고에서 어떤 키워드와 함께 언급되는지 분석
        </p>
      </div>

      {/* Skill selector */}
      <div className="mb-6">
        <select
          value={selectedSkill}
          onChange={(e) => setSelectedSkill(e.target.value)}
          className="rounded-lg border border-border-default bg-bg-surface px-4 py-2.5 text-sm text-text-primary"
        >
          <option value="" disabled>스킬 선택...</option>
          {skillOptions.map((skill) => (
            <option key={skill} value={skill}>{skill}</option>
          ))}
        </select>
      </div>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <>
          {/* KPI Cards */}
          <div className="mb-6 grid grid-cols-4 gap-4">
            <KpiCard
              label="스킬"
              value={data.skillName}
              icon={<Network className="h-5 w-5" />}
            />
            <KpiCard
              label="총 공고 수"
              value={data.totalPostingMentions.toLocaleString()}
              icon={<TrendingUp className="h-5 w-5" />}
            />
            <KpiCard
              label="연관 키워드 수"
              value={data.allKeywords.length}
              icon={<Hash className="h-5 w-5" />}
            />
            <KpiCard
              label="카테고리"
              value={data.category}
            />
          </div>

          {/* Force-Directed Graph */}
          {graphData.nodes.length > 0 && (
            <div className="mb-6 rounded-xl border border-border-default bg-bg-surface p-6">
              <h3 className="mb-4 text-lg font-semibold">키워드 관계 그래프</h3>
              <div className="overflow-hidden rounded-lg" style={{ backgroundColor: '#0d1117' }}>
                <ForceGraph2D
                  ref={graphRef}
                  graphData={graphData}
                  width={800}
                  height={450}
                  nodeCanvasObject={nodeCanvasObject}
                  nodeLabel="label"
                  nodeVal="val"
                  linkColor={() => 'rgba(139, 148, 158, 0.2)'}
                  linkWidth={1}
                  cooldownTicks={100}
                  d3AlphaDecay={0.05}
                  d3VelocityDecay={0.3}
                  backgroundColor="#0d1117"
                />
              </div>
              {/* Graph legend */}
              {data.keywordGroups && Object.keys(data.keywordGroups).length > 0 && (
                <div className="mt-3 flex flex-wrap gap-3">
                  {Object.entries(GROUP_COLORS).map(([group, color]) => {
                    if (!data.keywordGroups?.[group]) return null
                    return (
                      <div key={group} className="flex items-center gap-1.5 text-xs text-text-muted">
                        <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                        {group}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {/* Treemap */}
          {treemapData.length > 0 && (
            <div className="mb-6 rounded-xl border border-border-default bg-bg-surface p-6">
              <h3 className="mb-4 text-lg font-semibold">키워드 트리맵</h3>
              <ResponsiveContainer width="100%" height={400}>
                <Treemap
                  data={treemapData}
                  dataKey="size"
                  nameKey="name"
                  content={<TreemapContent x={0} y={0} width={0} height={0} name="" fill="" />}
                >
                  <Tooltip
                    formatter={(value: number | undefined) => [`${value ?? 0}건`, '공고 수']}
                    contentStyle={{
                      backgroundColor: 'var(--color-bg-surface)',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: '8px',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                </Treemap>
              </ResponsiveContainer>
            </div>
          )}

          {/* Keyword groups */}
          {data.keywordGroups && Object.keys(data.keywordGroups).length > 0 && (
            <div className="mb-6 grid grid-cols-2 gap-4">
              {Object.entries(data.keywordGroups).map(([group, keywords]) => (
                <div key={group} className="rounded-xl border border-border-default bg-bg-surface p-4">
                  <h4 className="mb-3 text-sm font-semibold text-accent-blue">{group}</h4>
                  <div className="flex flex-wrap gap-2">
                    {keywords.map((kw) => (
                      <span
                        key={kw.keyword}
                        className="rounded-full bg-bg-elevated px-3 py-1 text-xs font-medium text-text-primary"
                      >
                        {kw.keyword} ({kw.postingCount})
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Table */}
          <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border-default bg-bg-elevated text-text-muted">
                  <th className="px-4 py-3 text-left font-medium">#</th>
                  <th className="px-4 py-3 text-left font-medium">키워드</th>
                  <th className="px-4 py-3 text-right font-medium">공고 수</th>
                  <th className="px-4 py-3 text-right font-medium">비율</th>
                </tr>
              </thead>
              <tbody>
                {data.allKeywords.map((kw, idx) => (
                  <tr key={kw.keyword} className="border-b border-border-muted transition-colors hover:bg-bg-elevated">
                    <td className="px-4 py-3 font-mono text-text-muted">{idx + 1}</td>
                    <td className="px-4 py-3 font-mono font-medium">{kw.keyword}</td>
                    <td className="px-4 py-3 text-right font-mono">{kw.postingCount}</td>
                    <td className="px-4 py-3 text-right font-mono">{kw.percentage.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </motion.div>
  )
}
