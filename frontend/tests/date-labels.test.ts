import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test'
import { effectScope, ref } from 'vue'
import dayjs from 'dayjs'
import { useDate } from '../app/shared/composables/useDate'

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
afterEach(() => { dayjs.locale('en'); vi.unstubAllGlobals(); vi.restoreAllMocks() })
describe('SSR date label formatting', () => {
  it('uses Russian week boundaries and labels regardless of global dayjs locale', () => {
    const scope = effectScope()
    dayjs.locale('en')
    const dates = scope.run(() => useDate())!
    expect(dates.formatDate('2026-09-27', { type: 'date' })).toBe('Сегодня')
    expect(dates.formatDate('2026-10-02', { type: 'date' })).toBe('2 окт')
    expect(dates.formatDate('2026-09-24', { type: 'date' })).toBe('Четверг')
    dayjs.locale('ru')
    expect(dates.formatDate('2026-10-02', { type: 'date' })).toBe('2 окт')
    scope.stop()
  })
  it('does not rely on locale registration shared between SSR dayjs module instances', () => {
    const scope = effectScope()
    // SSR bundlers can load locale registration against a different Dayjs instance.
    const ru = dayjs.Ls.ru
    delete dayjs.Ls.ru
    try {
      dayjs.locale('en')
      const dates = scope.run(() => useDate())!
      expect(dates.formatDate('2026-10-02', { type: 'date' })).toBe('2 окт')
      expect(dates.formatDate('2026-09-24', { type: 'date' })).toBe('Четверг')
    } finally {
      dayjs.Ls.ru = ru!
      scope.stop()
    }
  })
  it('keeps a calendar date intact and renders UTC timestamps with the shared hydration offset', () => {
    const scope = effectScope()
    const dates = scope.run(() => useDate())!
    expect(dates.parseDate('2026-10-02', { type: 'date' })?.format('YYYY-MM-DD')).toBe('2026-10-02')
    expect(dates.formatDate('2026-10-02T23:30:00Z', { disableRelative: true })).toBe('3 окт 01:30')
    expect(dates.formatDate('2026-10-02', { type: 'date', format: 'YYYY-MM-DD' })).toBe('2026-10-02')
    scope.stop()
  })
  it('supports independent reactive locales without changing the global locale', () => {
    const scope = effectScope()
    const locale = ref<'ru' | 'en'>('ru')
    const dates = scope.run(() => useDate(locale))!
    const value = dates.parseDate('2026-10-02', { type: 'date' })
    expect(dates.formatDate(value, { type: 'date', disableRelative: true })).toBe('2 окт')
    locale.value = 'en'
    expect(dates.formatDate(value, { type: 'date', disableRelative: true })).toBe('2 Oct')
    expect(dayjs.locale()).toBe('en')
    scope.stop()
  })
})
