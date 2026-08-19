import type { Dayjs } from 'dayjs'

export type SmartQuickDate = {
  id: string
  label: string
  value: string
}

export type SmartRelativePreset = {
  id: string
  label: string
  expression: string
  periodSeconds: number
}

const RELATIVE_RE = /^now(?:-(\d+)([smhdw]))?$/i
const ABSOLUTE_FORMATS = [
  'YYYY-MM-DD HH:mm:ss',
  'YYYY-MM-DD HH:mm',
  'YYYY-MM-DD',
  'DD.MM.YYYY HH:mm:ss',
  'DD.MM.YYYY HH:mm',
  'DD.MM.YYYY',
]

const UNIT_SECONDS: Record<string, number> = {
  s: 1,
  m: 60,
  h: 3600,
  d: 86_400,
  w: 604_800,
}

export const SMART_RELATIVE_PRESETS: SmartRelativePreset[] = [
  { id: '5m', label: 'Последние 5 минут', expression: 'now-5m', periodSeconds: 5 * 60 },
  { id: '15m', label: 'Последние 15 минут', expression: 'now-15m', periodSeconds: 15 * 60 },
  { id: '30m', label: 'Последние 30 минут', expression: 'now-30m', periodSeconds: 30 * 60 },
  { id: '1h', label: 'Последний 1 час', expression: 'now-1h', periodSeconds: 3600 },
  { id: '3h', label: 'Последние 3 часа', expression: 'now-3h', periodSeconds: 3 * 3600 },
  { id: '6h', label: 'Последние 6 часов', expression: 'now-6h', periodSeconds: 6 * 3600 },
  { id: '12h', label: 'Последние 12 часов', expression: 'now-12h', periodSeconds: 12 * 3600 },
  { id: '24h', label: 'Последние 24 часа', expression: 'now-24h', periodSeconds: 24 * 3600 },
  { id: '2d', label: 'Последние 2 дня', expression: 'now-2d', periodSeconds: 2 * 86_400 },
  { id: '7d', label: 'Последние 7 дней', expression: 'now-7d', periodSeconds: 7 * 86_400 },
  { id: '30d', label: 'Последние 30 дней', expression: 'now-30d', periodSeconds: 30 * 86_400 },
  { id: '90d', label: 'Последние 90 дней', expression: 'now-90d', periodSeconds: 90 * 86_400 },
]

export const SMART_QUICK_DATES: SmartQuickDate[] = [
  { id: 'now', label: 'Сейчас', value: 'now' },
  ...SMART_RELATIVE_PRESETS.map((item) => ({
    id: item.id,
    label: item.label,
    value: item.expression,
  })),
]

export const SMART_DATE_ERROR = 'Некорректная дата. Используйте now, now-1h или YYYY-MM-DD HH:mm:ss'

export const useSmartDate = () => {
  const dayjs = useDayjs()

  const parseRelativeOffsetSeconds = (value: string): number | null => {
    const match = value.trim().match(RELATIVE_RE)
    if (!match) return null
    if (!match[1] || !match[2]) return 0
    const amount = Number(match[1])
    const unit = match[2].toLowerCase()
    const unitSeconds = UNIT_SECONDS[unit]
    if (!unitSeconds || Number.isNaN(amount)) return null
    return amount * unitSeconds
  }

  const parseExpression = (value: string, base = dayjs()): Dayjs | null => {
    const trimmed = value.trim()
    if (!trimmed) return null

    const relativeSeconds = parseRelativeOffsetSeconds(trimmed)
    if (relativeSeconds !== null) {
      return base.subtract(relativeSeconds, 'second')
    }

    for (const format of ABSOLUTE_FORMATS) {
      const parsed = dayjs(trimmed, format, true)
      if (parsed.isValid()) return dayjs(parsed.toDate())
    }

    const fallback = dayjs(trimmed)
    return fallback.isValid() ? fallback : null
  }

  const formatAbsolute = (value: Dayjs) => value.format('YYYY-MM-DD HH:mm:ss')

  const findQuickDate = (value?: string | null) => {
    const trimmed = value?.trim()
    if (!trimmed) return null
    return SMART_QUICK_DATES.find((item) => item.value === trimmed) ?? null
  }

  const getDateLabel = (value?: string | null) => {
    const trimmed = value?.trim()
    if (!trimmed) return 'Дата'
    const quick = findQuickDate(trimmed)
    if (quick) return quick.label
    const parsed = parseExpression(trimmed)
    if (parsed) return formatAbsolute(parsed)
    return trimmed
  }

  return {
    parseRelativeOffsetSeconds,
    parseExpression,
    formatAbsolute,
    findQuickDate,
    getDateLabel,
  }
}
