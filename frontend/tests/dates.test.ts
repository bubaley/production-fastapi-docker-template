import { describe, expect, it } from 'vite-plus/test'
import {
  localDateValue,
  resolveDateExpression,
  resolvePickerValue,
  validatePickerValues,
} from '../app/shared/ui/app/date-picker/dateMath'
import { finishCalendarRange, replaceCalendarDay } from '../app/shared/ui/app/date-picker/selection'
describe('date picker values', () => {
  it('round-trips date-only values without applying UTC shifts', () => {
    expect(localDateValue(resolvePickerValue('2026-09-27')!)).toBe('2026-09-27')
    expect(resolvePickerValue('2026-02-30')).toBeNull()
  })
  it('clamps month arithmetic and resolves relative range endpoints with one clock', () => {
    const now = new Date(2026, 2, 31, 14, 30)
    expect(localDateValue(resolveDateExpression('now-1M', now)!)).toBe('2026-02-28')
    expect(validatePickerValues(['now-1h', 'now'], { smart: true }, now)).toBeNull()
    expect(validatePickerValues(['now', 'now-1h'], { smart: true }, now)).toBe('order')
    expect(validatePickerValues(['now'], {}, now)).toBe('invalid')
  })
  it('includes the whole upper-bound date and validates partial ranges explicitly', () => {
    expect(validatePickerValues(['2026-09-27T23:59:59'], { max: '2026-09-27' })).toBeNull()
    expect(validatePickerValues(['2026-09-28'], { max: '2026-09-27' })).toBe('bounds')
    expect(validatePickerValues([null, '2026-09-27'], { allowPartial: true })).toBeNull()
    expect(validatePickerValues([null, '2026-09-27'], {})).toBe('invalid')
  })
  it('orders calendar gestures and retains the chosen endpoint clock', () => {
    expect(finishCalendarRange('2026-09-27', '2026-09-01')).toEqual({ start: '2026-09-01', end: '2026-09-27' })
    expect(replaceCalendarDay('2026-09-01', '2026-09-27T15:45', true)).toBe('2026-09-01T15:45')
  })
})
