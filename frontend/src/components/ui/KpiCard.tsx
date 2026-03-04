import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KpiCardProps {
  label: string
  value: string | number
  delta?: number
  deltaLabel?: string
  icon?: React.ReactNode
}

export function KpiCard({ label, value, delta, deltaLabel, icon }: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-border-default bg-bg-surface p-5"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm text-text-muted">{label}</span>
        {icon && <span className="text-text-subtle">{icon}</span>}
      </div>
      <div className="mt-2 font-mono text-3xl font-bold tracking-tight">
        {value}
      </div>
      {delta !== undefined && (
        <div className="mt-2 flex items-center gap-1 text-sm">
          {delta > 0 ? (
            <TrendingUp className="h-4 w-4 text-accent-green" />
          ) : delta < 0 ? (
            <TrendingDown className="h-4 w-4 text-accent-red" />
          ) : (
            <Minus className="h-4 w-4 text-text-subtle" />
          )}
          <span className={delta > 0 ? 'text-accent-green' : delta < 0 ? 'text-accent-red' : 'text-text-subtle'}>
            {delta > 0 ? '+' : ''}{delta}%
          </span>
          {deltaLabel && <span className="text-text-subtle">{deltaLabel}</span>}
        </div>
      )}
    </motion.div>
  )
}
