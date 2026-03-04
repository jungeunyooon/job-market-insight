import { type ReactNode } from 'react'

type Variant = 'default' | 'critical' | 'high' | 'medium' | 'low' | 'maintained' | 'continue' | 'active' | 'closed'

const variants: Record<Variant, string> = {
  default: 'bg-bg-elevated text-text-muted border-border-default',
  critical: 'bg-red-950 text-red-400 border-red-800',
  high: 'bg-amber-950 text-amber-400 border-amber-800',
  medium: 'bg-yellow-950 text-yellow-400 border-yellow-800',
  low: 'bg-teal-950 text-teal-400 border-teal-800',
  maintained: 'bg-green-950 text-green-400 border-green-800',
  continue: 'bg-blue-950 text-blue-400 border-blue-800',
  active: 'bg-green-950 text-green-400 border-green-800',
  closed: 'bg-red-950 text-red-400 border-red-800',
}

interface BadgeProps {
  variant?: Variant
  children: ReactNode
  className?: string
}

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}
