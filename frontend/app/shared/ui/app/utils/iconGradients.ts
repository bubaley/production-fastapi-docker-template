export type AppIconGradientSeverity = 'purple' | 'pink' | 'orange' | 'green' | 'blue' | 'cyan' | 'red'

export const APP_ICON_GRADIENT_STOPS: Record<AppIconGradientSeverity, string[]> = {
  purple: ['#6366f1', '#8b5cf6', '#a855f7', '#c084fc'],
  pink: ['#db2777', '#ec4899', '#f472b6', '#e879f9'],
  orange: ['#ea580c', '#f97316', '#fb923c', '#fbbf24'],
  green: ['#059669', '#10b981', '#34d399', '#2dd4bf'],
  blue: ['#2563eb', '#3b82f6', '#60a5fa', '#38bdf8'],
  cyan: ['#0e7490', '#06b6d4', '#22d3ee', '#67e8f9'],
  red: ['#b91c1c', '#ef4444', '#f87171', '#fb7185'],
}

export const appIconLinearGradient = (severity: AppIconGradientSeverity) =>
  `linear-gradient(120deg, ${APP_ICON_GRADIENT_STOPS[severity].join(', ')})`

export const appIconConicGradient = (severity: AppIconGradientSeverity) => {
  const stops = APP_ICON_GRADIENT_STOPS[severity]
  return `conic-gradient(${[...stops, stops[0]].join(', ')})`
}
