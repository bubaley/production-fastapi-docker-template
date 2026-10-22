import type { Component } from 'vue'
import type { ColorToken } from '../../template/types/template-ui-tokens'

export const EMPTY_DATA_LABEL = '—'
export type AppLabelTone = 'muted' | 'info' | 'warning' | 'primary' | 'positive' | 'destructive'
export type AppSemanticColor = ColorToken | AppLabelTone

export type AppLabelConfig = {
  label: string
  icon: string | Component
  color?: AppSemanticColor
  tone?: AppLabelTone
  unknown?: boolean
}

export const semanticColorClasses: Record<AppSemanticColor, string> = {
  primary: 'text-primary',
  cloud: 'text-muted-foreground',
  secondary: 'text-muted-foreground',
  muted: 'text-muted-foreground',
  info: 'text-info',
  danger: 'text-destructive',
  destructive: 'text-destructive',
  success: 'text-positive',
  positive: 'text-positive',
  warning: 'text-warning',
  orange: 'text-orange-500',
  yellow: 'text-yellow-500',
  teal: 'text-teal-500',
  pink: 'text-pink-500',
}

export const UNKNOWN_LABEL: AppLabelConfig = {
  label: 'Не удалось определить',
  icon: 'lucide:circle-question-mark',
  color: 'secondary',
  unknown: true,
}

export const semanticColorVariables: Record<AppSemanticColor, string> = {
  primary: 'var(--primary)',
  cloud: 'var(--muted-foreground)',
  secondary: 'var(--muted-foreground)',
  muted: 'var(--muted-foreground)',
  info: 'var(--ds-info)',
  warning: 'var(--ds-warning)',
  danger: 'var(--destructive)',
  destructive: 'var(--destructive)',
  success: 'var(--ds-positive)',
  positive: 'var(--ds-positive)',
  orange: 'var(--color-orange-500)',
  yellow: 'var(--color-yellow-500)',
  teal: 'var(--color-teal-500)',
  pink: 'var(--color-pink-500)',
}
