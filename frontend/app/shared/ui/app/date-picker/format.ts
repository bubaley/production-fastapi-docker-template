import { CalendarDateTime, parseTime } from '@internationalized/date'
import { formatDatePattern, parseDatePattern } from '~/shared/lib/dateFormat'
import { resolvePickerValue } from './dateMath'

const fromDate = (date: Date) =>
  new CalendarDateTime(
    date.getFullYear(),
    date.getMonth() + 1,
    date.getDate(),
    date.getHours(),
    date.getMinutes(),
    date.getSeconds(),
  )
export const DEFAULT_DATE_MASK = 'DD.MM.YYYY HH:mm'
/** Keep clock entry in HH:mm shape while allowing a single-digit hour before a colon. */
export function maskClockInput(value: string, seconds = false): string {
  const singleHour = value.match(/^\D*(\d)\s*:/)
  const digits = value.replace(/\D/g, '').slice(0, seconds ? 6 : 4)
  if (singleHour)
    return `0${singleHour[1]}:${digits.slice(1, 3)}${seconds && digits.length > 3 ? `:${digits.slice(3, 5)}` : ''}`
  return digits.length > 2
    ? `${digits.slice(0, 2)}:${digits.slice(2, 4)}${seconds && digits.length > 4 ? `:${digits.slice(4, 6)}` : ''}`
    : digits
}
/** Date-first masks share their date/time sections with the compound field. Bracketed literals are preserved. */
export function maskParts(mask = DEFAULT_DATE_MASK) {
  const tokens = [...mask.matchAll(/\[[^\]]*\]|YYYY|YY|MMMM|MMM|MM|M|DD|D|HH|H|hh|h|mm|m|A|a|./g)]
  const firstTime = tokens.find((match) => /^(HH?|hh?|mm?|A|a)$/.test(match[0]))
  return firstTime
    ? { date: mask.slice(0, firstTime.index).replace(/[\s,T]+$/, ''), time: mask.slice(firstTime.index) }
    : { date: mask, time: 'HH:mm' }
}
export function formatPickerValue(
  value: string | null | undefined,
  mask = DEFAULT_DATE_MASK,
  time = false,
  locale = 'ru',
): string {
  if (!value) return ''
  if (value.startsWith('now')) return value
  const date = resolvePickerValue(value)
  if (!date) return value
  return formatDatePattern(fromDate(date), time && value.includes('T') ? mask : maskParts(mask).date, locale)
}
export function parsePickerText(
  text: string,
  mask = DEFAULT_DATE_MASK,
  time = false,
  locale = 'ru',
  smart = false,
): string | null | undefined {
  const value = text.trim()
  if (!value) return null
  if (value.startsWith('now')) return smart && resolvePickerValue(value) ? value : undefined
  const dateMask = maskParts(mask).date
  for (const format of time ? [...new Set([mask, dateMask])] : [dateMask]) {
    const parsed = parseDatePattern(value, format)
    if (!parsed) continue
    const result = formatDatePattern(
      parsed,
      format === dateMask ? 'YYYY-MM-DD' : format.includes('ss') ? 'YYYY-MM-DDTHH:mm:ss' : 'YYYY-MM-DDTHH:mm',
    )
    if (resolvePickerValue(result)) return result
  }
  return undefined
}
export function formatPickerTime(value: string, mask = DEFAULT_DATE_MASK, locale = 'ru') {
  const clock = parseTime(value)
  return formatDatePattern(
    new CalendarDateTime(2000, 1, 1, clock.hour, clock.minute, clock.second),
    maskParts(mask).time,
    locale,
  )
}
