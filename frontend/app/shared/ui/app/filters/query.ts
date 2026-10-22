import type { ViewFilters, FilterValue } from './types'
/** Remove unfinished draft rows, retaining false, zero, and typed arrays. */
export function compactViewFilters(filters: ViewFilters): ViewFilters {
  return Object.fromEntries(
    Object.entries(filters).filter(
      ([, value]) => value !== '' && value != null && (!Array.isArray(value) || value.length > 0)
    )
  )
}
export function unlockedViewFilters(filters: ViewFilters, lockedFilters: ViewFilters = {}): ViewFilters {
  const canonicalField = (key: string) => key.split('__')[0]!.replace(/_id$/, '')
  const lockedFields = new Set(Object.keys(lockedFilters).map(canonicalField))
  return Object.fromEntries(Object.entries(filters).filter(([key]) => !lockedFields.has(canonicalField(key))))
}
export function tableViewFiltersToQueryParams(
  filters: ViewFilters,
  lockedFilters: ViewFilters = {}
): Record<string, string | number | boolean> {
  return Object.fromEntries(
    Object.entries(compactViewFilters({ ...unlockedViewFilters(filters, lockedFilters), ...lockedFilters })).map(
      ([key, value]) => [key, Array.isArray(value) ? value.join(',') : value]
    )
  )
}

/** Compare AND maps independent of insertion order and set-valued selection order. */
export function viewFiltersEqual(left: ViewFilters, right: ViewFilters): boolean {
  const canonical = (filters: ViewFilters) =>
    JSON.stringify(
      Object.entries(compactViewFilters(filters))
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, value]) => [
          key,
          Array.isArray(value) ? [...value].sort((a, b) => String(a).localeCompare(String(b))) : value
        ])
    )
  return canonical(left) === canonical(right)
}

/** Keep the operand when changing compatible operators; convert scalar/list shape. */
export function filterOperand(
  value: FilterValue | undefined,
  from: string,
  to: string,
  booleanField = false
): FilterValue {
  if (to === 'isnull' || booleanField) return typeof value === 'boolean' ? value : true
  const previous = from === 'isnull' ? undefined : value
  if (to === 'in' || to === 'not_in')
    return Array.isArray(previous)
      ? previous
      : previous !== undefined && previous !== '' && typeof previous !== 'boolean'
        ? [previous]
        : []
  return Array.isArray(previous) ? (previous[0] ?? '') : (previous ?? '')
}
