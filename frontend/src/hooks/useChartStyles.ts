import { useSyncExternalStore, useCallback } from 'react'

/** Subscribe to theme changes by watching the root element's class list */
function subscribe(cb: () => void) {
  const observer = new MutationObserver(cb)
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
  return () => observer.disconnect()
}

function getSnapshot() {
  return document.documentElement.classList.contains('light') ? 'light' : 'dark'
}

function getCssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

/** Reactive chart colors that update when theme changes */
export function useChartStyles() {
  const theme = useSyncExternalStore(subscribe, getSnapshot)

  // Re-compute on theme change (theme is in dependency via useSyncExternalStore)
  const colors = useCallback(() => ({
    tooltipBg: getCssVar('--dp-tooltip-bg'),
    tooltipBorder: getCssVar('--dp-tooltip-border'),
    tooltipText: getCssVar('--dp-tooltip-text'),
    gridStroke: getCssVar('--dp-grid-stroke'),
    axisStroke: getCssVar('--dp-axis-stroke'),
    axisTick: getCssVar('--dp-axis-tick'),
    axisLabel: getCssVar('--dp-axis-label'),
    bgElevated: getCssVar('--dp-bg-elevated'),
    accentBlue: getCssVar('--dp-accent-blue'),
  }), [theme]) // eslint-disable-line react-hooks/exhaustive-deps

  const c = colors()

  const tooltipStyle = {
    backgroundColor: c.tooltipBg,
    border: `1px solid ${c.tooltipBorder}`,
    borderRadius: 8,
    color: c.tooltipText,
    fontFamily: 'JetBrains Mono',
  }

  const xAxisProps = {
    tick: { fill: c.axisTick, fontSize: 12 },
    axisLine: { stroke: c.axisStroke },
    tickLine: { stroke: c.axisStroke },
  }

  const yAxisProps = {
    tick: { fill: c.axisLabel, fontSize: 13, fontFamily: 'JetBrains Mono' },
    axisLine: false as const,
    tickLine: false as const,
  }

  const gridProps = {
    strokeDasharray: '3 3',
    stroke: c.gridStroke,
    horizontal: false as const,
  }

  return { ...c, tooltipStyle, xAxisProps, yAxisProps, gridProps, theme }
}
