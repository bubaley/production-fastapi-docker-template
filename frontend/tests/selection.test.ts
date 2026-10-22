import { afterEach, describe, expect, it, vi } from 'vitest'
import { effectScope, nextTick, reactive, ref } from 'vue'
import { useSelectSource } from '../app/shared/ui/app/select/useSelectSource'
import { conditionRows, writeCondition } from '../app/shared/ui/app/filters/filterConditions'
import { tableViewFiltersToQueryParams } from '../app/shared/ui/app/filters/query'
import type { ViewFilterField } from '../app/shared/ui/app/filters/types'

const response = (ids: number[], hasNext = false) => ({ items: ids.map(id => ({ id })), pagination: { page: 1, size: 30, total: ids.length, pages: 1, has_next: hasNext } })
const deferred = () => {
  let resolve!: (value: ReturnType<typeof response>) => void
  const promise = new Promise<ReturnType<typeof response>>(done => { resolve = done })
  return { promise, resolve }
}
afterEach(() => vi.useRealTimers())
describe('select repository source', () => {
  it('clears options and never remembers pending results from a previous user context', async () => {
    const pending = deferred()
    const repo = reactive({ revision: 0, list: vi.fn().mockReturnValue(pending.promise) })
    const remember = vi.fn()
    const scope = effectScope()
    const source = scope.run(() => useSelectSource(() => ({ repo }), ref(true), ref(''), (item: { id: number }) => item.id, remember))!
    repo.revision++
    pending.resolve(response([1]))
    await nextTick()
    expect(source.items.value).toEqual([])
    expect(remember).not.toHaveBeenCalled()
    expect(source.loading.value).toBe(false)
    scope.stop()
  })
  it('ignores stale search responses and passes isolated pagination', async () => {
    vi.useFakeTimers()
    const first = deferred()
    const second = deferred()
    const list = vi.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise)
    const scope = effectScope()
    const search = ref('')
    const remember = vi.fn()
    const source = scope.run(() => useSelectSource(() => ({ repo: { list }, extraParams: { organization_id: 'a' }, debounce: 10 }), ref(true), search, (item: { id: number }) => item.id, remember))!
    search.value = 'new'
    await vi.advanceTimersByTimeAsync(10)
    second.resolve(response([2]))
    await nextTick()
    first.resolve(response([1]))
    await nextTick()
    expect(source.items.value).toEqual([{ id: 2 }])
    expect(remember).toHaveBeenCalledTimes(1)
    expect(list.mock.calls[1]).toEqual([{ organization_id: 'a', search: 'new' }, { storeInRepo: false, pagination: { page: 1, size: 30, total: 0, pages: 0, has_next: false } }])
    scope.stop()
  })
  it('deduplicates appended pages and stops on an empty server page', async () => {
    const list = vi.fn().mockResolvedValueOnce(response([1, 2], true)).mockResolvedValueOnce(response([2, 3], true)).mockResolvedValueOnce(response([], true))
    const scope = effectScope()
    const source = scope.run(() => useSelectSource(() => ({ repo: { list } }), ref(true), ref(''), (item: { id: number }) => item.id, () => {}))!
    await nextTick()
    source.loadMore()
    await nextTick()
    expect(source.items.value.map(item => item.id)).toEqual([1, 2, 3])
    source.loadMore()
    await nextTick()
    expect(source.hasMore.value).toBe(false)
    expect(list.mock.calls[2]![1].pagination.page).toBe(3)
    scope.stop()
  })
  it('exposes swallowed repo failures and retries the same page', async () => {
    const list = vi.fn().mockResolvedValueOnce(undefined).mockResolvedValueOnce(response([1]))
    const scope = effectScope()
    const source = scope.run(() => useSelectSource(() => ({ repo: { list } }), ref(true), ref(''), (item: { id: number }) => item.id, () => {}))!
    await nextTick()
    expect(source.error.value).toBeInstanceOf(Error)
    source.retry()
    await nextTick()
    expect(source.items.value).toEqual([{ id: 1 }])
    expect(source.error.value).toBeNull()
    scope.stop()
  })
})
describe('filter condition migration', () => {
  const field: ViewFilterField = { field: 'created_at', label: 'Дата', kind: 'datetime', lookups: ['gte', 'lte'] }
  it('keeps a date range atomic when changing and removing its operator', () => {
    const filters = writeCondition({}, field, 'range', 'range', ['2026-09-01', '2026-09-27'])
    expect(conditionRows([field], filters)).toMatchObject([{ lookup: 'range', value: ['2026-09-01T00:00:00', '2026-09-27T23:59:59'] }])
    expect(writeCondition(filters, field, 'range', null)).toEqual({})
    expect(writeCondition(filters, field, 'range', 'lte', ['a', 'b'])).toEqual({ created_at__lte: 'b' })
  })
  it('omits drafts while preserving false and zero in repo query params', () => {
    expect(tableViewFiltersToQueryParams({ enabled: false, amount: 0, draft: '', ids: [1, 2], empty: [] })).toEqual({ enabled: false, amount: 0, ids: '1,2' })
  })
})
