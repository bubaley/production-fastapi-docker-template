import dayjs, { type Dayjs } from 'dayjs'
import utc from 'dayjs/plugin/utc.js'
import ru from 'dayjs/locale/ru.js'
import en from 'dayjs/locale/en.js'
import { onMounted, ref, toValue, type MaybeRefOrGetter } from 'vue'

dayjs.extend(utc)
dayjs.locale(ru, undefined, true)
dayjs.locale(en, undefined, true)

export type DateFormat = 'shortcut'
export type DateType = 'date' | 'datetime'
export type DateLocale = 'ru' | 'en'

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

export const useDate = (locale: MaybeRefOrGetter<DateLocale> = 'ru') => {
  // Hydration shares the server clock/offset; local time is applied only after mounting.
  const reference = useState<number>('app-date-reference', () => Date.now())
  const offset = useState<number>('app-date-offset', () => dayjs().utcOffset())
  const mounted = ref(false)
  onMounted(() => {
    reference.value = Date.now()
    offset.value = dayjs().utcOffset()
    mounted.value = true
  })
  const localized = (value: Dayjs) => value.locale(toValue(locale))
  const now = (type: DateType = 'datetime') => {
    const value = localized(mounted.value ? dayjs(reference.value) : dayjs(reference.value).utcOffset(offset.value))
    return type === 'date' ? value.startOf('day') : value
  }
  const parseDate = (date?: string | null, config?: { isUtc?: boolean; type?: DateType }) => {
    if (!date) return null
    const { isUtc = true, type = 'datetime' } = config ?? {}
    // Calendar dates describe a day, not an instant, and must never shift across time zones.
    const calendarDate = type === 'date' || /^\d{4}-\d{2}-\d{2}$/.test(date)
    const value = mounted.value
      ? calendarDate ? dayjs(date.slice(0, 10)) : isUtc ? dayjs.utc(date).local() : dayjs(date)
      : calendarDate
      ? dayjs.utc(date.slice(0, 10)).utcOffset(offset.value, true)
      : isUtc
        ? dayjs.utc(date).utcOffset(offset.value)
        : dayjs.utc(date).utcOffset(offset.value, true)
    return value.isValid() ? localized(type === 'date' ? value.startOf('day') : value) : null
  }
  const relativeDay = (date: Dayjs, config?: { disableRelativeDay?: boolean; useShortWeekday?: boolean }) => {
    const current = now('date')
    const diff = date.startOf('day').diff(current, 'day')
    const relative = RELATIVE_DAYS[toValue(locale)][diff]
    if (!config?.disableRelativeDay && relative) return relative
    const firstWeekday = toValue(locale) === 'ru' ? 1 : 0
    const weekStart = current.subtract((current.day() - firstWeekday + 7) % 7, 'day')
    const day = date.startOf('day')
    if (day.isBefore(weekStart) || day.isAfter(weekStart.add(6, 'day'))) return null
    const labels = config?.useShortWeekday ? WEEKDAYS_SHORT : WEEKDAYS
    return labels[toValue(locale)][date.day()] ?? null
  }
  const formatDate = (
    input: Dayjs | null | string,
    config?: {
      format?: DateFormat | string
      type?: DateType
      includeSeconds?: boolean
      disableRelativeDay?: boolean
      useShortWeekday?: boolean
      disableRelative?: boolean
    },
  ): string | null => {
    const { format = 'shortcut', type = 'datetime' } = config ?? {}
    const date = typeof input === 'string' ? parseDate(input, { type }) : input ? localized(input) : null
    if (!date) return null
    if (format !== 'shortcut') return date.format(format)
    const relative = config?.disableRelative ? null : relativeDay(date, config)
    const year = date.year() === now().year() ? '' : ` ${date.format('YYYY')}`
    const label = relative ?? `${date.date()} ${MONTHS_SHORT[toValue(locale)][date.month()]}${year}`
    return type === 'date' ? label : `${label} ${date.format(config?.includeSeconds ? 'HH:mm:ss' : 'HH:mm')}`
  }
  return { parseDate, formatDate, now }
}
