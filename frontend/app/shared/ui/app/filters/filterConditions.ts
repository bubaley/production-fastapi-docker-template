import type { FilterValue, ViewFilterField, ViewFilters } from './types'
import { filterOperand } from './query'
export const supportsDateRange = (field: ViewFilterField) =>
  ['date', 'datetime'].includes(field.kind) && field.lookups.includes('gte') && field.lookups.includes('lte')
export function conditionRows(fields: ViewFilterField[], filters: ViewFilters) {
  const seen = new Set<string>()
  return Object.entries(filters).flatMap(([key, value]) => {
    const field = fields.find((field) => field.field === key.split('__')[0])
    if (!field) return []
    const lookup = key.split('__')[1] || 'exact'
    if (
      supportsDateRange(field) &&
      ['gte', 'lte'].includes(lookup) &&
      `${field.field}__gte` in filters &&
      `${field.field}__lte` in filters
    ) {
      if (seen.has(field.field)) return []
      seen.add(field.field)
      return [
        {
          key: `${field.field}__gte`,
          field,
          lookup: 'range',
          value: [
            String(filters[`${field.field}__gte`] ?? ''),
            String(filters[`${field.field}__lte`] ?? '')
          ] as FilterValue
        }
      ]
    }
    return [{ key, field, lookup, value }]
  })
}
export function dateFilterValue(value: string | null, time: boolean, end: boolean) {
  if (!value) return ''
  // Relative expressions are stored verbatim; only calendar dates get default time boundaries.
  return time && /^\d{4}-\d{2}-\d{2}$/.test(value) ? `${value}T${end ? '23:59:59' : '00:00:00'}` : value
}
export function writeCondition(
  filters: ViewFilters,
  field: ViewFilterField,
  from: string,
  to: string | null,
  value?: FilterValue
): ViewFilters {
  const key = (lookup: string) => (lookup === 'exact' ? field.field : `${field.field}__${lookup}`)
  const removed = from === 'range' ? [key('gte'), key('lte')] : [key(from), ...(from === 'exact' ? [`${field.field}__exact`] : [])]
  const next = Object.fromEntries(Object.entries(filters).filter(([name]) => !removed.includes(name)))
  if (to === null) return next
  if (to === 'range') {
    const values = Array.isArray(value) ? value : from === 'lte' ? ['', value ?? ''] : [value ?? '', '']
    next[key('gte')] = dateFilterValue(String(values[0] ?? ''), field.kind === 'datetime', false)
    next[key('lte')] = dateFilterValue(String(values[1] ?? ''), field.kind === 'datetime', true)
  } else
    next[key(to)] = filterOperand(
      from === 'range' && Array.isArray(value) ? value[to === 'lte' || to === 'lt' ? 1 : 0] : value,
      from,
      to,
      field.kind === 'boolean'
    )
  return next
}
