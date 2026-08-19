import { SMART_RELATIVE_PRESETS, useSmartDate } from '~/shared/ui/app/smartDatePicker/composables/useSmartDate'

export type SmartDateRange = {
  from: string
  to: string
  quickRangeId?: string | null
}

export type SmartQuickRange = {
  id: string
  label: string
  from: string
  to: string
  periodSeconds: number
}

export const SMART_DATE_RANGE_DEFAULT: SmartDateRange = {
  from: 'now-1h',
  to: 'now',
  quickRangeId: '1h',
}

export const SMART_QUICK_RANGES: SmartQuickRange[] = SMART_RELATIVE_PRESETS.map((item) => ({
  id: item.id,
  label: item.label,
  from: item.expression,
  to: 'now',
  periodSeconds: item.periodSeconds,
}))

export const useSmartDateRange = () => {
  const dayjs = useDayjs()
  const { parseExpression, parseRelativeOffsetSeconds, formatAbsolute } = useSmartDate()

  const resolveRange = (range: SmartDateRange, base = dayjs()) => {
    const end = parseExpression(range.to, base)
    const start = parseExpression(range.from, base)
    if (!start || !end) return null
    if (!end.isAfter(start) && !end.isSame(start)) return null

    const periodSeconds = Math.max(1, end.diff(start, 'second'))
    return { start, end, periodSeconds }
  }

  /** Period length ending at "now" — matches analytics APIs that only accept lookback seconds. */
  const resolveLookbackSeconds = (range: SmartDateRange, base = dayjs()) => {
    const start = parseExpression(range.from, base)
    if (!start) return null
    return Math.max(1, base.diff(start, 'second'))
  }

  const getQuickRange = (id?: string | null) => {
    if (!id) return null
    return SMART_QUICK_RANGES.find((item) => item.id === id) ?? null
  }

  const findQuickRangeByExpressions = (from: string, to: string) => {
    return SMART_QUICK_RANGES.find((item) => item.from === from.trim() && item.to === to.trim()) ?? null
  }

  const getRangeLabel = (range: SmartDateRange) => {
    const quick = getQuickRange(range.quickRangeId) ?? findQuickRangeByExpressions(range.from, range.to)
    if (quick) return quick.label

    const resolved = resolveRange(range)
    if (!resolved) return `${range.from} → ${range.to}`
    return `${formatAbsolute(resolved.start)} — ${formatAbsolute(resolved.end)}`
  }

  const toRangeFromQuick = (quick: SmartQuickRange): SmartDateRange => ({
    from: quick.from,
    to: quick.to,
    quickRangeId: quick.id,
  })

  const toRangeFromPeriodSeconds = (periodSeconds: number): SmartDateRange => {
    const quick = SMART_QUICK_RANGES.find((item) => item.periodSeconds === periodSeconds)
    if (quick) return toRangeFromQuick(quick)

    const unit =
      periodSeconds % 86_400 === 0
        ? `${periodSeconds / 86_400}d`
        : periodSeconds % 3600 === 0
          ? `${periodSeconds / 3600}h`
          : periodSeconds % 60 === 0
            ? `${periodSeconds / 60}m`
            : `${periodSeconds}s`

    return {
      from: `now-${unit}`,
      to: 'now',
      quickRangeId: null,
    }
  }

  return {
    parseExpression,
    parseRelativeOffsetSeconds,
    formatAbsolute,
    resolveRange,
    resolveLookbackSeconds,
    getQuickRange,
    findQuickRangeByExpressions,
    getRangeLabel,
    toRangeFromQuick,
    toRangeFromPeriodSeconds,
  }
}
