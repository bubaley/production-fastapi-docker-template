import 'dayjs/locale/ru'

import type { Dayjs } from "dayjs"

// import Dayjs from 'dayjs-nuxt'
export type DateFormat = 'shortcut'
export type DateType = 'date' | 'datetime'

const RELATIVE_DAYS: Record<number, string> = {
  [-2]: 'Позавчера',
  [-1]: 'Вчера',
  0: 'Сегодня',
  1: 'Завтра',
  2: 'Послезавтра'
}

const MONTHS_SHORT = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']

const WEEKDAYS_SHORT = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

export const useDate = () => {
  const dayjs = useDayjs()
  dayjs.locale('ru')
  const now = (type: DateType = 'datetime') => {
    return type === 'date' ? dayjs().startOf('day') : dayjs()
  }

  const parseDate = (date?: string | null, config?: { isUtc?: boolean; type?: DateType }) => {
    if (!date) return null
    const { isUtc = true, type = 'datetime' } = config ?? {}
    let value = isUtc ? dayjs.utc(date).local() : dayjs(date)
    if (type === 'date') value = value.startOf('day')
    return value.isValid() ? value : null
  }

  const getDaysDifference = (date: Dayjs): number => {
    const dateStart = date.startOf('day')
    const nowStart = now().startOf('day')
    return dateStart.diff(nowStart, 'day')
  }

  const isWithinCurrentWeek = (date: Dayjs): boolean => {
    const dateStart = date.startOf('day')
    const nowStart = now().startOf('day')
    const weekStart = nowStart.startOf('week')
    const weekEnd = weekStart.add(6, 'day')
    return (
      (dateStart.isSame(weekStart) || dateStart.isAfter(weekStart)) &&
      (dateStart.isSame(weekEnd) || dateStart.isBefore(weekEnd))
    )
  }

  // const isWithinNextWeek = (date: Dayjs): boolean => {
  //   const dateStart = date.startOf('day')
  //   const nowStart = now().startOf('day')
  //   const nextWeekStart = nowStart.add(1, 'week').startOf('week')
  //   const nextWeekEnd = nextWeekStart.add(6, 'day')
  //   return (
  //     (dateStart.isSame(nextWeekStart) || dateStart.isAfter(nextWeekStart)) &&
  //     (dateStart.isSame(nextWeekEnd) || dateStart.isBefore(nextWeekEnd))
  //   )
  // }

  const formatWeekday = (date: Dayjs): string => {
    return date.format('dddd')
  }

  const formatShortWeekday = (date: Dayjs): string => {
    const dayIndex = date.day()
    return WEEKDAYS_SHORT[dayIndex] || 'вс'
  }

  const formatRelativeDay = (
    date: Dayjs,
    config?: {
      disableRelativeDay?: boolean
      useShortWeekday?: boolean
    }
  ): string | null => {
    const diff = getDaysDifference(date)

    if (!config?.disableRelativeDay && RELATIVE_DAYS[diff]) {
      return RELATIVE_DAYS[diff]
    }

    // if (isWithinCurrentWeek(date) || isWithinNextWeek(date)) {
    if (isWithinCurrentWeek(date)) {
      if (config?.useShortWeekday) {
        return formatShortWeekday(date)
      }
      const weekdayName = formatWeekday(date)
      return weekdayName.charAt(0).toUpperCase() + weekdayName.slice(1)
    }

    return null
  }

  const formatDateWithMonth = (date: Dayjs, includeYear: boolean = false): string => {
    const day = date.format('D')
    const monthIndex = date.month()
    const month = MONTHS_SHORT[monthIndex]
    const year = includeYear ? ` ${date.format('YYYY')}` : ''
    return `${day} ${month}${year}`
  }

  const formatTime = (date: Dayjs, includeSeconds: boolean = false): string => {
    return includeSeconds ? date.format('HH:mm:ss') : date.format('HH:mm')
  }

  const formatShortcutDate = (
    date: Dayjs,
    config?: {
      disableRelative?: boolean
      disableRelativeDay?: boolean
      useShortWeekday?: boolean
    }
  ): string => {
    let relative: string | null = null
    if (!config?.disableRelative) relative = formatRelativeDay(date, config)
    if (relative) return relative
    const isCurrentYear = date.year() === now().year()
    return formatDateWithMonth(date, !isCurrentYear)
  }

  const formatDate = (
    date: Dayjs | null | string,
    config?: {
      format?: DateFormat | string
      type?: DateType
      includeSeconds?: boolean
      disableRelativeDay?: boolean
      useShortWeekday?: boolean
      disableRelative?: boolean
    }
  ): string | null => {
    if (typeof date === 'string') date = parseDate(date)
    if (!date) return null
    const { format = 'shortcut', type = 'datetime' } = config ?? {}
    date = date.isUTC() ? date.local() : date

    const values: string[] = []
    if (format === 'shortcut') values.push(formatShortcutDate(date, config))
    if (type === 'datetime') values.push(formatTime(date, config?.includeSeconds))
    return values.join(' ')
  }

  return {
    parseDate,
    formatDate,
    now
  }
}
