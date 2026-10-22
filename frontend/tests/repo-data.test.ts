import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test'
import { effectScope, nextTick, reactive, ref, watchEffect } from 'vue'
import { useRepoData } from '../app/shared/toolkits/repo/composables/useRepoData'
import { filterBySearch } from '../app/shared/utils/filterUtils'

const pagination = (page = 1) => ({ page, size: 20, total: 40, pages: 2, has_next: page < 2 })
const response = (ids: number[], page = 1) => ({
  items: ids.map((id) => ({ id, name: String(id) })),
  pagination: pagination(page),
})
const deferred = () => {
  let resolve!: (value: ReturnType<typeof response>) => void
  let reject!: (reason: Error) => void
  const promise = new Promise<ReturnType<typeof response>>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
beforeEach(() => {
  vi.stubGlobal('paginationFromServer', (raw = {}) => ({
    page: 1,
    size: 50,
    total: 0,
    pages: 0,
    has_next: false,
    ...raw,
  }))
  vi.stubGlobal('filterBySearch', filterBySearch)
  vi.spyOn(console, 'warn').mockImplementation(() => {})
})
afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})
describe('repository data state', () => {
  it('clears a user context and ignores its pending list response', async () => {
    const pending = deferred()
    const repo = reactive({
      revision: 0,
      list: vi
        .fn()
        .mockResolvedValueOnce(response([1]))
        .mockReturnValueOnce(pending.promise),
    })
    const scope = effectScope()
    const state = scope.run(() => useRepoData({ repo: repo as never, autoLoad: false }))!
    await state.loadItems()
    const oldRequest = state.loadItems()
    repo.revision++
    expect(state.items.value).toEqual([])
    pending.resolve(response([2]))
    await oldRequest
    expect(state.items.value).toEqual([])
    expect(state.error.value).toBeNull()
    expect(state.loading.value).toBe(false)
    scope.stop()
  })
  it('notifies rendering effects when list events push, replace, delete and edit rows', async () => {
    const repo = { list: vi.fn().mockResolvedValue(response([1])) }
    const scope = effectScope()
    let rendered = ''
    const state = scope.run(() => {
      const state = useRepoData<{ id: number; name: string }>({ repo: repo as never, autoLoad: false })
      watchEffect(() => {
        rendered = state.items.value.map((item) => item.name).join(',')
      })
      return state
    })!
    await state.loadItems()
    await nextTick()
    expect(rendered).toBe('1')
    state.items.value.push({ id: 2, name: 'new' })
    await nextTick()
    expect(rendered).toBe('1,new')
    state.items.value.splice(0, 1, { id: 1, name: 'saved' })
    await nextTick()
    expect(rendered).toBe('saved,new')
    state.items.value[0]!.name = 'edited'
    await nextTick()
    expect(rendered).toBe('edited,new')
    state.items.value.splice(1, 1)
    await nextTick()
    expect(rendered).toBe('edited')
    scope.stop()
  })
  it('clears rows synchronously on context change while retaining search refresh rows', async () => {
    vi.useFakeTimers()
    const repo = { list: vi.fn().mockResolvedValue(response([1])), items: [] }
    const context = ref({ organization_id: 'old' })
    const scope = effectScope()
    const state = scope.run(() =>
      useRepoData<{ id: number; name: string }>({
        repo: repo as never,
        extraParams: context,
        debounce: 30,
        autoLoad: false,
        storeInRepo: true,
      }),
    )!
    await state.loadItems()
    state.search.value = 'query'
    expect(state.items.value).toHaveLength(1)
    context.value.organization_id = 'new'
    expect(state.items.value).toEqual([])
    expect(repo.items).toEqual([])
    expect(state.pagination.value.page).toBe(1)
    scope.stop()
  })
  it('invalidates old results immediately when context changes, before debounce runs', async () => {
    vi.useFakeTimers()
    const first = deferred()
    const second = deferred()
    const repo = {
      list: vi.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise),
      pagination: pagination(2),
      items: [],
    }
    const context = ref({ organization_id: 'old' })
    const scope = effectScope()
    const state = scope.run(() =>
      useRepoData<{ id: number; name: string }>({
        repo: repo as never,
        extraParams: context,
        debounce: 30,
        autoLoad: false,
      }),
    )!
    const previous = state.loadItems({}, { pagination: pagination(2) })
    context.value = { organization_id: 'new' }
    first.resolve(response([1], 2))
    await previous
    expect(state.items.value).toEqual([])
    expect(state.pagination.value.page).toBe(1)
    await vi.advanceTimersByTimeAsync(30)
    second.resolve(response([2]))
    await nextTick()
    expect(state.items.value.map((item) => item.id)).toEqual([2])
    expect(repo.list.mock.calls[1]![0]).toEqual({ organization_id: 'new' })
    expect(repo.list.mock.calls[1]![1].pagination.page).toBe(1)
    expect(repo.pagination.page).toBe(2)
    expect(repo.items).toEqual([])
    scope.stop()
  })
  it('ignores stale errors and clears previous errors as soon as search changes', async () => {
    vi.useFakeTimers()
    const old = deferred()
    const repo = {
      list: vi
        .fn()
        .mockResolvedValueOnce(undefined)
        .mockReturnValueOnce(old.promise)
        .mockResolvedValue(response([3])),
    }
    const scope = effectScope()
    const state = scope.run(() =>
      useRepoData<{ id: number; name: string }>({ repo: repo as never, debounce: 25, autoLoad: false }),
    )!
    await expect(state.loadItems()).rejects.toThrow('Не удалось загрузить данные')
    expect(state.error.value).toBeInstanceOf(Error)
    state.search.value = 'new'
    expect(state.error.value).toBeNull()
    await vi.advanceTimersByTimeAsync(25)
    state.search.value = 'latest'
    old.reject(new Error('old request'))
    await nextTick()
    expect(state.error.value).toBeNull()
    await vi.advanceTimersByTimeAsync(25)
    expect(state.items.value.map((item) => item.id)).toEqual([3])
    expect(state.loading.value).toBe(false)
    scope.stop()
  })
  it('keeps pagination object independent from a response and publishes only accepted data', async () => {
    const result = response([1], 2)
    const repo = { list: vi.fn().mockResolvedValue(result), items: [], pagination: pagination() }
    const scope = effectScope()
    const state = scope.run(() =>
      useRepoData<{ id: number; name: string }>({ repo: repo as never, autoLoad: false, storeInRepo: true }),
    )!
    await state.loadItems()
    state.pagination.value.page = 4
    expect(result.pagination.page).toBe(2)
    expect(repo.pagination.page).toBe(2)
    expect(repo.items).toEqual(result.items)
    expect(repo.list.mock.calls[0]![1].storeInRepo).toBe(false)
    scope.stop()
  })
  it('filters reactive local items and accessor functions without losing zero-valued IDs', async () => {
    const items = ref([
      { id: 0, name: 'Zero' },
      { id: 1, name: 'One' },
    ])
    const scope = effectScope()
    const state = scope.run(() => useRepoData({ items, itemLabel: (item) => item.name, autoLoad: false }))!
    state.search.value = 'zero'
    expect(state.items.value).toEqual([{ id: 0, name: 'Zero' }])
    items.value = [{ id: 2, name: 'Zero two' }]
    await nextTick()
    expect(state.items.value).toEqual([{ id: 2, name: 'Zero two' }])
    scope.stop()
  })
})
