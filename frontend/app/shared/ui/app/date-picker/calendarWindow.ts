import { CalendarDate } from '@internationalized/date'

export const WEEK_HEIGHT = 40
export const MONTH_CHROME_HEIGHT = 68
export const WINDOW_RADIUS = 120
export type CalendarMonth = { key: string; value: CalendarDate; top: number; height: number; weeks: number }
export function monthIndex(date: { year: number; month: number }) {
  return (date.year - 1) * 12 + date.month - 1
}
export function monthAt(index: number) {
  return new CalendarDate(Math.floor(index / 12) + 1, (index % 12) + 1, 1)
}
export function monthWindow(center: number) {
  const first = Math.max(0, center - WINDOW_RADIUS)
  const last = Math.min(9999 * 12 - 1, center + WINDOW_RADIUS)
  let top = 0
  const months: CalendarMonth[] = []
  for (let index = first; index <= last; index++) {
    const value = monthAt(index)
    // Gregorian Julian day 0 is a Monday; avoid local timezone/DST calculations.
    const weekday = value.calendar.toJulianDay(value) % 7
    const weeks = Math.ceil((weekday + value.calendar.getDaysInMonth(value)) / 7)
    const height = MONTH_CHROME_HEIGHT + weeks * WEEK_HEIGHT
    months.push({ key: value.toString(), value, top, height, weeks })
    top += height
  }
  return { first, months, height: top }
}
export function visibleMonthIndex(months: CalendarMonth[], scrollTop: number) {
  let low = 0,
    high = months.length - 1
  while (low < high) {
    const mid = Math.floor((low + high) / 2)
    if (months[mid]!.top + months[mid]!.height <= scrollTop) low = mid + 1
    else high = mid
  }
  return low
}
export function monthWeeks(month: CalendarMonth) {
  const offset = month.value.calendar.toJulianDay(month.value) % 7
  const first = month.value.subtract({ days: offset })
  return Array.from({ length: month.weeks }, (_, row) =>
    Array.from({ length: 7 }, (_, col) => first.add({ days: row * 7 + col })),
  )
}
