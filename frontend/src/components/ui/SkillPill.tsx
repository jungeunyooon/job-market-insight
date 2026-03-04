interface SkillPillProps {
  name: string
  className?: string
}

export function SkillPill({ name, className = '' }: SkillPillProps) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-md border border-border-default bg-bg-elevated px-2 py-0.5 font-mono text-xs text-text-primary ${className}`}>
      {name}
    </span>
  )
}
