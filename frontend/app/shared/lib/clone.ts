import { toRaw } from 'vue'

/**
 * Deep copy of plain data (objects, arrays, dates, primitives) that also accepts Vue reactive proxies.
 * `structuredClone` alone throws on proxies, including proxies nested inside raw objects.
 */
export function deepClone<T>(value: T): T {
  const raw = toRaw(value) as unknown
  if (Array.isArray(raw)) return raw.map((item) => deepClone(item)) as T
  if (raw instanceof Date) return new Date(raw.getTime()) as T
  if (raw && typeof raw === 'object') {
    const proto = Object.getPrototypeOf(raw)
    if (proto === Object.prototype || proto === null) {
      return Object.fromEntries(Object.entries(raw).map(([key, item]) => [key, deepClone(item)])) as T
    }
    return structuredClone(raw) as T
  }
  return raw as T
}
