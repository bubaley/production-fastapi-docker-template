import { CalendarDate, parseDate, parseDateTime } from '@internationalized/date'

/** Resolve once per operation, so both relative range endpoints share the same clock. */
export function resolveDateExpression(value: string, now = new Date()): Date | null {
  if (!/^now(?:[+-]\d+[smhdwMy])*(?:\/[dhMwy])?$/.test(value)) return null
  if (!Number.isFinite(now.getTime())) return null
  const result = new Date(now)
  for (const match of value.matchAll(/([+-])(\d+)([smhdwMy])/g)) {
    const amount = Number(match[2]) * (match[1] === '+' ? 1 : -1)
    if (!Number.isSafeInteger(amount) || Math.abs(amount) > 100000) return null
    const unit = match[3]
    if (unit === 'M' || unit === 'y') {
      const date = new CalendarDate(result.getFullYear(), result.getMonth() + 1, result.getDate()).add(
        unit === 'M' ? { months: amount } : { years: amount },
      )
      result.setFullYear(date.year, date.month - 1, date.day)
    } else if (unit === 'd' || unit === 'w') result.setDate(result.getDate() + amount * (unit === 'w' ? 7 : 1))
    else result.setTime(result.getTime() + amount * ({ s: 1000, m: 60000, h: 3600000 }[unit!] || 0))
  }
  const round = value.split('/')[1]
  if (round) {
    result.setMinutes(0, 0, 0)
    if (round !== 'h') result.setHours(0)
    if (round === 'w') result.setDate(result.getDate() - ((result.getDay() + 6) % 7))
    if (round === 'M' || round === 'y') result.setDate(1)
    if (round === 'y') result.setMonth(0)
  }
  return Number.isFinite(result.getTime()) && result.getFullYear() > 0 && result.getFullYear() <= 9999 ? result : null
}
export function localDateValue(date: Date, time = false): string {
  const day = [
    date.getFullYear().toString().padStart(4, '0'),
    String(date.getMonth() + 1).padStart(2, '0'),
    String(date.getDate()).padStart(2, '0'),
  ].join('-')
  return time ? `${day}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}` : day
}
export function resolvePickerValue(value: string | null | undefined, now = new Date()): Date | null {
  if (!value) return null
  if (value.startsWith('now')) return resolveDateExpression(value, now)
  try {
    if (!/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?)?$/.test(value)) return null
    const parsed = value.includes('T') ? parseDateTime(value) : parseDate(value)
    if (parsed.year < 1) return null
    const result = new Date(0)
    result.setFullYear(parsed.year, parsed.month - 1, parsed.day)
    result.setHours(
      'hour' in parsed ? parsed.hour : 0,
      'minute' in parsed ? parsed.minute : 0,
      'second' in parsed ? parsed.second : 0,
      0,
    )
    return result
  } catch {
    return null
  }
}
export function calendarValue(value: string | null | undefined) {
  const date = resolvePickerValue(value)
  return date ? parseDate(localDateValue(date)) : undefined
}
export function validatePickerValues(
  values: (string | null)[],
  options: { smart?: boolean; min?: string; max?: string; allowPartial?: boolean },
  now = new Date(),
): 'invalid' | 'order' | 'bounds' | null {
  const dates = (options.allowPartial ? values.filter((value): value is string => !!value) : values).map((value) =>
    !options.smart && value?.startsWith('now') ? null : resolvePickerValue(value, now),
  )
  if (dates.some((date) => !date)) return 'invalid'
  if (dates.length === 2 && dates[0]! > dates[1]!) return 'order'
  const min = resolvePickerValue(options.min, now)
  const max = resolvePickerValue(options.max, now)
  // Date-only upper bounds include their entire local day.
  if (max && options.max?.length === 10) max.setHours(23, 59, 59, 999)
  if (dates.some((date) => (min && date! < min) || (max && date! > max))) return 'bounds'
  return null
}
