import { computed, onScopeDispose, ref, toValue, watch, type Ref } from 'vue'
import type { ViewFilters } from '../../app/filters/types'
import type { AppListDataProps } from '../types/template-types'
import type { ResourceForm, ResourceItem } from '~/shared/api/resource'
import { useResourceList } from '~/shared/api/useResource'
import { filterBySearch } from '~/shared/utils/filterUtils'

/**
 * Rows for `AppListTemplate`: with a resource, an infinite query keyed by search + filters + `extraParams`
 * (a change starts at page 1); without one, `items` filtered locally.
 */
export function useListData<T extends ResourceItem, F extends ResourceForm>(
  props: () => AppListDataProps<T, F>,
  filters: Ref<ViewFilters>,
) {
  const remote = Boolean(props().resource) && !props().onlyClientSearch
  const search = ref('')
  const appliedSearch = ref('')
  const loadRequested = ref(false)
  let timer: ReturnType<typeof setTimeout> | undefined
  watch(search, (value) => {
    clearTimeout(timer)
    const delay = remote ? (props().debounce ?? 400) : 0
    if (delay) timer = setTimeout(() => (appliedSearch.value = value), delay)
    else appliedSearch.value = value
  })
  onScopeDispose(() => clearTimeout(timer))

  const params = computed(() => ({
    ...(appliedSearch.value ? { [props().searchParam ?? 'search']: appliedSearch.value } : {}),
    ...filters.value,
    ...toValue(props().extraParams ?? {}),
  }))

  const list = remote
    ? useResourceList(() => props().resource!, {
        params,
        pageSize: () => props().pageSize,
        enabled: () => props().autoLoad !== false || loadRequested.value,
      })
    : null

  const access = (item: T, accessor?: string | ((v: T) => string)) =>
    typeof accessor === 'function'
      ? accessor(item)
      : accessor
        ? (item as Record<string, unknown>)[accessor]
        : (item as Record<string, unknown>).name
  const localItems = computed(() => {
    const items = props().items ?? []
    const term = appliedSearch.value
    if (!term.trim()) return items
    const fields = props().filterFields?.length ? props().filterFields! : [props().itemLabel]
    return filterBySearch(term, items, (item) =>
      fields
        .map((field) => String(access(item, field as string | ((v: T) => string) | undefined) ?? ''))
        .join(' ')
        .toLowerCase(),
    )
  })

  const reload = async () => {
    if (!list) return
    loadRequested.value = true
    await list.refetch()
  }
  const loadMore = async () => {
    if (!list || list.isLoading.value) return
    if (list.hasNextPage.value) await list.loadNextPage()
    else if (list.error.value) await list.refetch()
  }

  return {
    search,
    remote,
    items: computed<T[]>(() => (list ? list.items.value : localItems.value)),
    loading: computed(() => list?.isLoading.value ?? false),
    error: computed(() => list?.error.value ?? null),
    hasNextPage: computed(() => list?.hasNextPage.value ?? false),
    loadMore,
    reload,
  }
}
