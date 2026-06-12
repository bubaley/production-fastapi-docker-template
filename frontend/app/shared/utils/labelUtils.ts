import type { LabelConfig } from "../types/label-types"

export type LabelConfigWithValues<T extends string | number | symbol> = LabelConfig & { value: T }

/** Класс цвета для иконки по семантике `LabelConfig.color` (Prime / Tailwind). */
export const labelColorToIconClass = (color: LabelConfig['color']): string => {
  const map: Record<LabelConfig['color'], string> = {
    primary: 'text-primary-500',
    secondary: 'fg-secondary',
    success: 'text-green-500',
    info: 'text-sky-500',
    warn: 'text-amber-500',
    help: 'text-violet-500',
    danger: 'text-red-500',
    contrast: 'text-surface-950 dark:text-surface-0',
  }
  return map[color]
}

export const getLabelConfigsWithValues = <T extends string | number | symbol>(values: Record<T, LabelConfig>) => {
  const result: LabelConfigWithValues<T>[] = Object.entries(values).map(([value, labelConfig]) => {
    return {
      ...labelConfig as LabelConfig,
      value: value as T,
    }
  })
  return result
}
