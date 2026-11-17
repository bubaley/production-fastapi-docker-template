import { computed, onScopeDispose, ref, shallowRef, watch, type Ref } from 'vue'
import { mergeItems } from './selection'
import type { SelectProps, SelectValue } from './types'

export function useSelectSource<T>(
  props: () => SelectProps<T>,
  open: Ref<boolean>,
  search: Ref<string>,
  key: (item: T) => SelectValue,
  remember: (items: T[]) => void,
) {
  const items = shallowRef<T[]>([])
  const loading = ref(false)
  const loadingPage = ref(0)
  const pending = ref(false)
  const error = shallowRef<unknown>(null)
  const page = ref(0)
  const hasMore = ref(false)
  let revision = 0
  let timer: ReturnType<typeof setTimeout> | undefined
  let failedPage = 1
  const invalidate = () => {
    revision++
    clearTimeout(timer)
    pending.value = false
    loading.value = false
  }
  const load = async (requestedPage: number) => {
    const source = props().source
    if (!source || (!open.value && !props().autoLoad) || props().disabled || loading.value) return
    const requestRevision = revision
    failedPage = requestedPage
    loading.value = true
    loadingPage.value = requestedPage
    pending.value = false
    error.value = null
    try {
      const result = await source.list(
        {
          ...props().extraParams,
          ...props().query,
          ...(!props().onlyClientSearch && search.value.trim()
            ? { [props().searchParam ?? 'search']: search.value.trim() }
            : {}),
        },
        { page: requestedPage, size: props().pageSize ?? 30 },
      )
      if (requestRevision !== revision || (!open.value && !props().autoLoad)) return
      remember(result.items)
      items.value = mergeItems(requestedPage === 1 ? [] : items.value, result.items, key)
      page.value = requestedPage
      // Empty pages end pagination even if the server reports an inconsistent has_next.
      hasMore.value = result.items.length > 0 && result.hasNext
    } catch (reason) {
      if (requestRevision === revision) {
        error.value = reason
        if (requestedPage === 1) items.value = []
      }
    } finally {
      if (requestRevision === revision) loading.value = false
    }
  }
  // Loaded options stay on screen until the new page 1 arrives (reopening, typing in the search): emptying the list
  // first collapsed the dropdown to a spinner and back, moving options under the pointer.
  const restart = (delay: boolean) => {
    invalidate()
    error.value = null
    page.value = 0
    hasMore.value = false
    if ((!open.value && !props().autoLoad) || !props().source || props().disabled) return
    if (delay) {
      pending.value = true
      timer = setTimeout(() => {
        void load(1)
      }, props().debounce ?? 300)
    } else void load(1)
  }
  // Another source has other options: nothing of the old one may stay.
  watch(
    () => props().source,
    () => {
      items.value = []
    },
    { flush: 'sync' },
  )
  watch([open, () => props().source, () => props().disabled, () => props().pageSize], () => restart(false), {
    immediate: true,
    flush: 'sync',
  })
  watch(
    () => JSON.stringify([props().query, props().extraParams]),
    () => restart(true),
    { flush: 'sync' },
  )
  watch(
    search,
    () => {
      if (!props().onlyClientSearch) restart(true)
    },
    { flush: 'sync' },
  )
  onScopeDispose(invalidate)
  return {
    items,
    loading,
    loadingMore: computed(() => loading.value && loadingPage.value > 1),
    pending,
    error,
    hasMore,
    loadMore: () => {
      if (hasMore.value && !pending.value && !error.value) void load(page.value + 1)
    },
    retry: () => {
      if (!pending.value) void load(failedPage)
    },
  }
}
