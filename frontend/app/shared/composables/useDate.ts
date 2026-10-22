import {
  CalendarDateTime,
  fromAbsolute,
  getLocalTimeZone,
  parseDate as parseCalendarDate,
  parseDateTime,
  toCalendarDate,
  toCalendarDateTime,
} from '@internationalized/date'
import { onMounted, ref, toValue, type MaybeRefOrGetter } from 'vue'
import { formatDatePattern } from '~/shared/lib/dateFormat'

export type DateFormat = 'shortcut'
export type DateType = 'date' | 'datetime'
export type DateLocale = 'ru' | 'en'
/** A wall-clock date and time in the viewer's zone (or the shared SSR offset before hydration). */
export type AppDateValue = CalendarDateTime

const RELATIVE_DAYS: Record<DateLocale, Record<number, string>> = {
  ru: { [-2]: 'Позавчера', [-1]: 'Вчера', 0: 'Сегодня', 1: 'Завтра', 2: 'Послезавтра' },
  en: { [-2]: 'Day before yesterday', [-1]: 'Yesterday', 0: 'Today', 1: 'Tomorrow', 2: 'Day after tomorrow' },
}
const MONTHS_SHORT = {
  ru: ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'],
  en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
}

const WEEKDAYS = {
  ru: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
  en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
}
const WEEKDAYS_SHORT = {
  ru: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  en: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
}

const pad = (value: number) => String(value).padStart(2, '0')
const startOfDay = (value: AppDateValue) => new CalendarDateTime(value.year, value.month, value.day)
/** 0 = Sunday … 6 = Saturday, independent of locale. */
const weekday = (value: AppDateValue) => new Date(Date.UTC(value.year, value.month - 1, value.day)).getUTCDay()
const currentOffset = () => -new Date().getTimezoneOffset()
const TIME_ZONE_SUFFIX = /(?:Z|[+-]\d{2}:?\d{2})$/i

/** Wall clock of an instant: in the local zone, or at a fixed UTC offset (minutes) for SSR/hydration. */
const wallClock = (instant: number, offset: number | null) =>
  offset === null
    ? toCalendarDateTime(fromAbsolute(instant, getLocalTimeZone()))
    : toCalendarDateTime(fromAbsolute(instant + offset * 60_000, 'UTC'))

export const useDate = (locale: MaybeRefOrGetter<DateLocale> = 'ru') => {
  // Hydration shares the server clock/offset; local time is applied only after mounting.
  const reference = useState<number>('app-date-reference', () => Date.now())
  const offset = useState<number>('app-date-offset', currentOffset)
  const mounted = ref(false)
  onMounted(() => {
    reference.value = Date.now()
    offset.value = currentOffset()
    mounted.value = true
  })
  const zoneOffset = () => (mounted.value ? null : offset.value)

  const now = (type: DateType = 'datetime') => {
    const value = wallClock(reference.value, zoneOffset())
    return type === 'date' ? startOfDay(value) : value
  }

  const parseDate = (date?: string | null, config?: { isUtc?: boolean; type?: DateType }): AppDateValue | null => {
    if (!date) return null
    const { isUtc = true, type = 'datetime' } = config ?? {}
    try {
      // Calendar dates describe a day, not an instant, and must never shift across time zones.
      if (type === 'date' || /^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return toCalendarDateTime(parseCalendarDate(date.slice(0, 10)))
      }
      const normalized = date.trim().replace(' ', 'T')
      const hasZone = TIME_ZONE_SUFFIX.test(normalized)
      if (!isUtc && !hasZone) return parseDateTime(normalized.slice(0, 19))
      const instant = Date.parse(hasZone ? normalized : `${normalized}Z`)
      return Number.isFinite(instant) ? wallClock(instant, zoneOffset()) : null
    } catch {
      return null
    }
  }

  const relativeDay = (date: AppDateValue, config?: { disableRelativeDay?: boolean; useShortWeekday?: boolean }) => {
    const current = now('date')
    const diff = toCalendarDate(date).compare(toCalendarDate(current))
    const relative = RELATIVE_DAYS[toValue(locale)][diff]
    if (!config?.disableRelativeDay && relative) return relative
    const firstWeekday = toValue(locale) === 'ru' ? 1 : 0
    const weekStart = current.subtract({ days: (weekday(current) - firstWeekday + 7) % 7 })
    const day = startOfDay(date)
    if (day.compare(weekStart) < 0 || day.compare(weekStart.add({ days: 6 })) > 0) return null
    const labels = config?.useShortWeekday ? WEEKDAYS_SHORT : WEEKDAYS
    return labels[toValue(locale)][weekday(date)] ?? null
  }

  const formatDate = (
    input: AppDateValue | null | string,
    config?: {
      /** `shortcut` (relative day or "2 окт") or a pattern such as `DD.MM.YYYY HH:mm`. */
      format?: DateFormat | string
      type?: DateType
      includeSeconds?: boolean
      disableRelativeDay?: boolean
      useShortWeekday?: boolean
      disableRelative?: boolean
    },
  ): string | null => {
    const { format = 'shortcut', type = 'datetime' } = config ?? {}
    const date = typeof input === 'string' ? parseDate(input, { type }) : input
    if (!date) return null
    if (format !== 'shortcut') return formatDatePattern(date, format, toValue(locale))
    const relative = config?.disableRelative ? null : relativeDay(date, config)
    const year = date.year === now().year ? '' : ` ${date.year}`
    const label = relative ?? `${date.day} ${MONTHS_SHORT[toValue(locale)][date.month - 1]}${year}`
    const time = `${pad(date.hour)}:${pad(date.minute)}${config?.includeSeconds ? `:${pad(date.second)}` : ''}`
    return type === 'date' ? label : `${label} ${time}`
  }
  return { parseDate, formatDate, now }
}
