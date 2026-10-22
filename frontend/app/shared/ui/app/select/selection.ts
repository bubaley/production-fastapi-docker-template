import type { SelectAccessor, SelectValue } from './types'

export function readItem<T, V>(item: T, accessor: SelectAccessor<T, V>): V {
  if (typeof accessor === 'function') return accessor(item)
  return accessor
    .split('.')
    .reduce<unknown>(
      (value, key) =>
        value != null && typeof value === 'object' ? (value as Record<string, unknown>)[key] : undefined,
      item
    ) as V
}
export function valueOf<T>(item: T, accessor: SelectAccessor<T, SelectValue>): SelectValue {
  const value = readItem(item, accessor)
  if (typeof value !== 'string' && typeof value !== 'number')
    throw new Error('AppSelect: item-value must resolve to a string or number')
  return value
}
export function normalizeSelection(value: unknown): unknown[] {
  return value == null ? [] : Array.isArray(value) ? value : [value]
}
export function selectionKey<T>(value: unknown, accessor: SelectAccessor<T, SelectValue>): SelectValue {
  return value != null && typeof value === 'object' ? valueOf(value as T, accessor) : (value as SelectValue)
}
export function mergeItems<T>(items: T[], appended: T[], key: (item: T) => SelectValue): T[] {
  return [...new Map([...items, ...appended].map((item) => [key(item), item])).values()]
}
