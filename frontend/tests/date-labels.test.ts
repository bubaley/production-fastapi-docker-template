import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test'
import { effectScope, ref } from 'vue'
import { useDate } from '../app/shared/composables/useDate'
import { formatDatePattern, parseDatePattern } from '../app/shared/lib/dateFormat'

beforeEach(() => {
  const states = new Map<string, ReturnType<typeof ref>>()
  states.set('app-date-reference', ref(Date.UTC(2026, 8, 27, 12)))
  states.set('app-date-offset', ref(120))
  vi.stubGlobal('useState', (key: string, initial: () => unknown) => {
    if (!states.has(key)) states.set(key, ref(initial()))
    return states.get(key)
  })
  vi.spyOn(console, 'warn').mockImplementation(() => {})
})
afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})
describe('SSR date label formatting', () => {
  it('uses Russian week boundaries and relative labels', () => {
    const scope = effectScope()
    const dates = scope.run(() => useDate())!
    expect(dates.formatDate('2026-09-27', { type: 'date' })).toBe('Сегодня')
    expect(dates.formatDate('2026-10-02', { type: 'date' })).toBe('2 окт')
    expect(dates.formatDate('2026-09-24', { type: 'date' })).toBe('Четверг')
    expect(dates.formatDate('2025-12-31', { type: 'date' })).toBe('31 дек 2025')
    scope.stop()
  })
  it('keeps a calendar date intact and renders UTC timestamps with the shared hydration offset', () => {
    const scope = effectScope()
    const dates = scope.run(() => useDate())!
    expect(dates.formatDate(dates.parseDate('2026-10-02', { type: 'date' }), { format: 'YYYY-MM-DD' })).toBe(
      '2026-10-02',
    )
    expect(dates.formatDate('2026-10-02T23:30:00Z', { disableRelative: true })).toBe('3 окт 01:30')
    expect(dates.formatDate('2026-10-02 23:30:00', { disableRelative: true })).toBe('3 окт 01:30')
    expect(dates.formatDate('2026-10-02T23:30:00+03:00', { disableRelative: true, includeSeconds: true })).toBe(
      '2 окт 22:30:00',
    )
    expect(dates.parseDate('2026-10-02T10:00:00', { isUtc: false })?.hour).toBe(10)
    expect(dates.parseDate('not a date')).toBeNull()
    scope.stop()
  })
  it('supports independent reactive locales', () => {
    const scope = effectScope()
    const locale = ref<'ru' | 'en'>('ru')
    const dates = scope.run(() => useDate(locale))!
    const value = dates.parseDate('2026-10-02', { type: 'date' })
    expect(dates.formatDate(value, { type: 'date', disableRelative: true })).toBe('2 окт')
    locale.value = 'en'
    expect(dates.formatDate(value, { type: 'date', disableRelative: true })).toBe('2 Oct')
    expect(dates.formatDate('2026-09-26', { type: 'date' })).toBe('Yesterday')
    scope.stop()
  })
})

describe('date patterns', () => {
  it('formats and strictly parses Day.js-style tokens', () => {
    const value = parseDatePattern('02.10.2026 09:05', 'DD.MM.YYYY HH:mm')!
    expect(formatDatePattern(value, 'YYYY-MM-DD[T]HH:mm')).toBe('2026-10-02T09:05')
    expect(formatDatePattern(value, 'D MMMM YYYY', 'ru')).toBe('2 октября 2026')
    expect(formatDatePattern(value, 'h:mm A')).toBe('9:05 AM')
    expect(parseDatePattern('30.02.2026', 'DD.MM.YYYY')).toBeNull()
    expect(parseDatePattern('2.10.2026', 'DD.MM.YYYY')).toBeNull()
    expect(parseDatePattern('2.10.2026', 'D.M.YYYY')?.day).toBe(2)
    expect(parseDatePattern('12:30 PM', 'hh:mm A')?.hour).toBe(12)
  })
})
