import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useActionState } from '../app/shared/composables/useActionState'

const toast = { default: vi.fn(), error: vi.fn() }
beforeEach(() => { vi.stubGlobal('useToast', () => toast); vi.clearAllMocks() })
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals() })
const deferred = () => {
  let resolve!: (value: string) => void
  const promise = new Promise<string>(done => { resolve = done })
  return { resolve, promise }
}
describe('action execution', () => {
  it('shares an in-flight execution and notifies once through toast.default', async () => {
    const request = deferred()
    const fn = vi.fn(() => request.promise)
    const action = useActionState(fn, { successNotification: value => ({ message: value, duration: 1500 }) })
    const first = action.execute('first')
    const second = action.execute('second')
    expect(first).toBe(second)
    expect(fn).toHaveBeenCalledTimes(1)
    expect(action.loading.value).toBe(true)
    request.resolve('Готово')
    await expect(first).resolves.toBe('Готово')
    expect(action.data.value).toBe('Готово')
    expect(action.loading.value).toBe(false)
    expect(toast.default).toHaveBeenCalledExactlyOnceWith('Готово', { duration: 1500 })
  })
  it('allows retry after synchronous failures and resets error on execution', async () => {
    const fn = vi.fn().mockImplementationOnce(() => { throw new Error('failure') }).mockReturnValueOnce('ok')
    const action = useActionState(fn, { errorNotification: 'Не удалось сохранить' })
    await expect(action.execute()).rejects.toThrow('failure')
    expect(action.error.value?.message).toBe('failure')
    expect(action.loading.value).toBe(false)
    const retry = action.execute()
    expect(action.error.value).toBeNull()
    await expect(retry).resolves.toBe('ok')
    expect(fn).toHaveBeenCalledTimes(2)
    expect(toast.error).toHaveBeenCalledExactlyOnceWith('Не удалось сохранить')
  })
  it('debounces latest arguments, settles every caller and prevents overlap after start', async () => {
    vi.useFakeTimers()
    const request = deferred()
    const fn = vi.fn(() => request.promise)
    const action = useActionState(fn, { debounce: 50 })
    const first = action.execute('old')
    await vi.advanceTimersByTimeAsync(30)
    const second = action.execute('latest')
    expect(second).toBe(first)
    await vi.advanceTimersByTimeAsync(49)
    expect(fn).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(1)
    expect(fn).toHaveBeenCalledExactlyOnceWith('latest')
    expect(action.execute('while running')).toBe(first)
    await vi.advanceTimersByTimeAsync(100)
    expect(fn).toHaveBeenCalledTimes(1)
    request.resolve('ok')
    await expect(first).resolves.toBe('ok')
    await expect(second).resolves.toBe('ok')
    expect(action.loading.value).toBe(false)
  })
})
