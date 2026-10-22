import { semanticColorClasses, type AppLabelConfig } from '../ui/app/types/label-types'

export type AppLabelConfigWithValues<T extends string | number | symbol> = AppLabelConfig & { value: T }

export const labelColorToIconClass = (color: AppLabelConfig['color']): string => {
  return color ? semanticColorClasses[color] : 'text-muted-foreground'
}

export const getLabelConfigsWithValues = <T extends string | number | symbol>(values: Record<T, AppLabelConfig>) => {
  const result: AppLabelConfigWithValues<T>[] = Object.entries(values).map(([value, labelConfig]) => {
    return {
      ...(labelConfig as AppLabelConfig),
      value: value as T,
    }
  })
  return result
}
