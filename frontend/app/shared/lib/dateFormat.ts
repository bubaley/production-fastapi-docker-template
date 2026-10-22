import { CalendarDateTime } from '@internationalized/date'

// Day.js-style patterns on top of @internationalized/date (wall-clock values, no time zone).
// Supported tokens: YYYY YY MMMM MMM MM M DD D HH H hh h mm m ss s A a, and [literal text].
const TOKEN = /\[[^\]]*\]|YYYY|YY|MMMM|MMM|MM|M|DD|D|HH|H|hh|h|mm|m|ss|s|A|a/g

const pad = (value: number, length = 2) => String(value).padStart(length, '0')
const utcDate = (value: CalendarDateTime) => new Date(Date.UTC(2000, value.month - 1, value.day))

const monthName = (value: CalendarDateTime, locale: string, style: 'short' | 'long') => {
  // `day` in the options yields the grammatical form used in dates (e.g. Russian genitive "октября").
  const parts = new Intl.DateTimeFormat(locale, { day: 'numeric', month: style, timeZone: 'UTC' }).formatToParts(
    utcDate(value),
  )
  return (parts.find((part) => part.type === 'month')?.value ?? '').replace(/\.$/, '')
}

export function formatDatePattern(value: CalendarDateTime, pattern: string, locale = 'ru'): string {
  const hour12 = value.hour % 12 || 12
  return pattern.replace(TOKEN, (token) => {
    switch (token) {
      case 'YYYY':
        return pad(value.year, 4)
      case 'YY':
        return pad(value.year % 100)
      case 'MMMM':
        return monthName(value, locale, 'long')
      case 'MMM':
        return monthName(value, locale, 'short')
      case 'MM':
        return pad(value.month)
      case 'M':
        return String(value.month)
      case 'DD':
        return pad(value.day)
      case 'D':
        return String(value.day)
      case 'HH':
        return pad(value.hour)
      case 'H':
        return String(value.hour)
      case 'hh':
        return pad(hour12)
      case 'h':
        return String(hour12)
      case 'mm':
        return pad(value.minute)
      case 'm':
        return String(value.minute)
      case 'ss':
        return pad(value.second)
      case 's':
        return String(value.second)
      case 'A':
        return value.hour < 12 ? 'AM' : 'PM'
      case 'a':
        return value.hour < 12 ? 'am' : 'pm'
      default:
        return token.slice(1, -1)
    }
  })
}

const NUMERIC: Record<string, string> = {
  YYYY: '(\\d{4})',
  YY: '(\\d{2})',
  MM: '(\\d{2})',
  M: '(\\d{1,2})',
  DD: '(\\d{2})',
  D: '(\\d{1,2})',
  HH: '(\\d{2})',
  H: '(\\d{1,2})',
  hh: '(\\d{2})',
  h: '(\\d{1,2})',
  mm: '(\\d{2})',
  m: '(\\d{1,2})',
  ss: '(\\d{2})',
  s: '(\\d{1,2})',
  A: '(AM|PM|am|pm)',
  a: '(AM|PM|am|pm)',
}
const escape = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

/** Strict parse of numeric patterns. Returns null when the text does not match or the date does not exist. */
export function parseDatePattern(text: string, pattern: string): CalendarDateTime | null {
  const tokens: string[] = []
  let source = ''
  let last = 0
  for (const match of pattern.matchAll(TOKEN)) {
    source += escape(pattern.slice(last, match.index))
    const token = match[0]
    if (token.startsWith('[')) source += escape(token.slice(1, -1))
    else if (NUMERIC[token]) {
      source += NUMERIC[token]
      tokens.push(token)
    } else return null
    last = match.index + token.length
  }
  source += escape(pattern.slice(last))
  const match = new RegExp(`^${source}$`).exec(text)
  if (!match) return null
  // Time-only patterns resolve to an arbitrary valid day.
  const parts = { year: 2000, month: 1, day: 1, hour: 0, minute: 0, second: 0 }
  let meridiem: string | undefined
  tokens.forEach((token, index) => {
    const raw = match[index + 1]!
    const value = Number(raw)
    if (token === 'YYYY') parts.year = value
    else if (token === 'YY') parts.year = 2000 + value
    else if (token.startsWith('M')) parts.month = value
    else if (token.startsWith('D')) parts.day = value
    else if (token.toLowerCase().startsWith('h')) parts.hour = value
    else if (token.startsWith('m')) parts.minute = value
    else if (token.startsWith('s')) parts.second = value
    else meridiem = raw.toLowerCase()
  })
  if (meridiem) {
    if (parts.hour < 1 || parts.hour > 12) return null
    parts.hour = (parts.hour % 12) + (meridiem === 'pm' ? 12 : 0)
  }
  if (parts.year < 1 || parts.month < 1 || parts.month > 12 || parts.hour > 23 || parts.minute > 59) return null
  if (parts.second > 59 || parts.day < 1) return null
  const result = new CalendarDateTime(parts.year, parts.month, 1, parts.hour, parts.minute, parts.second)
  if (parts.day > result.calendar.getDaysInMonth(result)) return null
  return result.set({ day: parts.day })
}
