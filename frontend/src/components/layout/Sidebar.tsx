import { NavLink } from 'react-router-dom'
import { BarChart3, Building2, GitCompare, Target, Search, Activity, Sun, Moon, Zap, BookOpen } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

const navItems = [
  { to: '/', icon: BarChart3, label: '스킬 랭킹' },
  { to: '/company', icon: Building2, label: '회사 프로필' },
  { to: '/compare', icon: GitCompare, label: '포지션 비교' },
  { to: '/gap', icon: Target, label: '갭 분석' },
  { to: '/search', icon: Search, label: '공고 검색' },
  { to: '/buzz', icon: Zap, label: 'Buzz vs 채용' },
  { to: '/blog-trend', icon: BookOpen, label: '블로그 트렌드' },
]

export function Sidebar() {
  const { theme, toggleTheme } = useTheme()

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-60 flex-col border-r border-border-default bg-bg-surface transition-colors">
      {/* Logo */}
      <div className="flex items-center gap-2.5 border-b border-border-default px-5 py-4">
        <Activity className="h-6 w-6 text-accent-blue" />
        <div>
          <h1 className="text-lg font-bold tracking-tight">DevPulse</h1>
          <p className="text-xs text-text-muted">채용시장 분석</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-accent-blue/10 text-accent-blue'
                  : 'text-text-muted hover:bg-bg-elevated hover:text-text-primary'
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-border-default px-5 py-4">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="mb-3 flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-text-muted transition-colors hover:bg-bg-elevated hover:text-text-primary"
        >
          {theme === 'dark' ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
          {theme === 'dark' ? '라이트 모드' : '다크 모드'}
        </button>

        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent-green" />
          <span className="text-xs text-text-muted">데모 모드</span>
        </div>
        <p className="mt-1 text-xs text-text-subtle">2026-03-04 스냅샷</p>
      </div>
    </aside>
  )
}
