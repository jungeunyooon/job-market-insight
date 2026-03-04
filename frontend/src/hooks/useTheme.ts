import { useState, useEffect, useCallback } from 'react'

type Theme = 'dark' | 'light'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('devpulse-theme')
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'light') {
      root.classList.add('light')
    } else {
      root.classList.remove('light')
    }
    localStorage.setItem('devpulse-theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }, [])

  return { theme, toggleTheme }
}

/** CSS variable values for Recharts inline styles (which can't use CSS vars directly) */
export function useChartColors() {
  const root = typeof document !== 'undefined' ? document.documentElement : null
  const get = (name: string) =>
    root ? getComputedStyle(root).getPropertyValue(name).trim() : ''

  return {
    tooltipBg: get('--dp-tooltip-bg') || '#21262d',
    tooltipBorder: get('--dp-tooltip-border') || '#30363d',
    tooltipText: get('--dp-tooltip-text') || '#e6edf3',
    gridStroke: get('--dp-grid-stroke') || '#21262d',
    axisStroke: get('--dp-axis-stroke') || '#30363d',
    axisTick: get('--dp-axis-tick') || '#7d8590',
    axisLabel: get('--dp-axis-label') || '#e6edf3',
  }
}
