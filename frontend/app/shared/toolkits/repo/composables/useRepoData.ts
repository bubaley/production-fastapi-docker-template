import { computed, onMounted, onScopeDispose, ref, shallowRef, toValue, watch, type MaybeRefOrGetter, type Ref } from 'vue'

export interface UseRepoDataProps<T> {
  repo?: AppRepo<T extends AppModel ? T : never>
  items?: T[]
  searchParam?: string
  debounce?: number
  onlyClientSearch?: boolean
  filterFields?: (keyof T)[]
  filter?: boolean
  extraParams?: MaybeRefOrGetter<Record<string, unknown>>
  autoLoad?: boolean
  storeInRepo?: boolean
  itemLabel?: string | ((v: T) => string)
  itemValue?: string | ((v: T) => string)
}

export const useRepoData = <T>(params: Omit<UseRepoDataProps<T>, 'items'> & { items?: Ref<T[] | undefined> }) => {
  const search = ref('')
  const data = ref(params.items?.value ?? []) as Ref<T[]>
  const pagination = ref<AppPagination>(paginationFromServer())
  const loading = ref(false)
  const error = shallowRef<Error | null>(null)
  const debounce = computed(() => params.repo && !params.onlyClientSearch ? (params.debounce ?? 400) : 0)
  let generation = 0
  let timer: ReturnType<typeof setTimeout> | undefined
  const access = (item: T | null | undefined, accessor?: string | ((v: T) => string)) => {
    if (item == null) return null
    return typeof accessor === 'function' ? accessor(item) : accessor ? (item as Record<string, unknown>)[accessor] : item
  }
  const getItemLabel = (item?: T | null) => access(item, params.itemLabel)
  const getItemValue = (item?: T | null) => access(item, params.itemValue)
  const clientFilter = (items: T[], term: string) => {
    if (!term.trim()) return items
    const fields = params.filterFields?.length ? params.filterFields : [params.itemLabel]
    return filterBySearch(term, items, (item) => fields.map(field => String(access(item, field as string) ?? '')).join(' ').toLowerCase())
  }
  const invalidate = () => {
    generation++
    clearTimeout(timer)
    loading.value = false
    error.value = null
  }
  const loadItems = async (query: Record<string, unknown> = {}, config: RepoListConfig = {}) => {
    invalidate()
    const request = generation
    loading.value = true
    error.value = null
    try {
      if (!params.repo || params.onlyClientSearch) {
        data.value = clientFilter(params.items?.value ?? [], search.value)
        return data.value
      }
      const page = config.pagination ?? pagination.value
      const result = await params.repo.list(
        { ...(search.value ? { [params.searchParam ?? 'search']: search.value } : {}), ...query, ...toValue(params.extraParams ?? {}) },
        { ...config, pagination: { ...page }, storeInRepo: false },
      )
      if (request !== generation) return data.value
      if (!result) throw new Error('Не удалось загрузить данные')
      pagination.value = { ...result.pagination }
      data.value = config.mode === 'append' ? [...data.value, ...result.items] : result.items
      if (params.storeInRepo) {
        params.repo.items = data.value as typeof params.repo.items
        params.repo.pagination = { ...result.pagination }
      }
      return data.value
    } catch (reason) {
      if (request !== generation) return data.value
      error.value = reason instanceof Error ? reason : new Error(String(reason))
      throw reason
    } finally {
      if (request === generation) loading.value = false
    }
  }
  const reload = () => {
    invalidate()
    pagination.value = paginationFromServer({ size: pagination.value.size })
    const run = () => { void loadItems().catch(() => {}) }
    if (debounce.value) timer = setTimeout(run, debounce.value)
    else run()
  }
  watch(search, reload, { flush: 'sync' })
  watch(() => params.repo?.revision, () => {
    invalidate()
    data.value = []
    pagination.value = paginationFromServer()
  }, { flush: 'sync' })
  watch(() => toValue(params.extraParams ?? {}), () => {
    data.value = []
    if (params.storeInRepo && params.repo) params.repo.items = []
    reload()
  }, { deep: true, flush: 'sync' })
  watch(() => params.items?.value, value => { data.value = clientFilter(value ?? [], search.value) })
  onMounted(() => {
    if (params.autoLoad !== false && params.repo) void loadItems().catch(() => {})
  })
  onScopeDispose(invalidate)
  const loadItemsState = { data, loading, error, execute: loadItems }
  return { items: data, search, pagination, loading, error, loadItemsState, debounce, loadItems, getItemLabel, getItemValue, clientFilter, itemLabel: params.itemLabel, itemValue: params.itemValue }
}
