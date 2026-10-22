import type { DatePickerRange } from './types'
export function replaceCalendarDay(day: string, previous: string | null | undefined, time: boolean) {
  const clock = time ? previous?.split('T')[1] : undefined
  return clock ? `${day}T${clock}` : day
}
/** Calendar gestures may run backwards; typed date-times are validated rather than silently reordered. */
export function finishCalendarRange(start: string, end: string): DatePickerRange {
  return start.slice(0, 10) > end.slice(0, 10) ? { start: end, end: start } : { start, end }
}
