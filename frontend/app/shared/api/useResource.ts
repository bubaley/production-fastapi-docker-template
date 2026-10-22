import { useInfiniteQuery, useMutation, useQuery, useQueryCache, type QueryCache } from '@pinia/colada'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'
import type { ApiClient } from './client'
import {
  DEFAULT_PAGE_SIZE,
  destroyItem,
  fetchItem,
  fetchPage,
  resourceKeys,
  saveItem,
  type ListQuery,
  type Resource,
  type ResourceForm,
  type ResourceItem,
} from './resource'

/** The request-scoped API client from `plugins/api.ts` (cookie forwarding on SSR, refresh-and-retry in the browser). */
export const useApiClient = (): ApiClient => useNuxtApp().$api

/**
 * Marks the resource's queries stale (active ones refetch) plus its `invalidates` roots. `exceptId` keeps the
 * detail entry of a record that was just written (its data is already set) or deleted (a refetch would 404).
 */
export const invalidateResource = (queryCache: QueryCache, resource: Resource<any, any, any, any>, exceptId?: string) =>
  Promise.all([
    queryCache.invalidateQueries({
      key: resourceKeys(resource).all,
      predicate: (entry) => !exceptId || entry.key[1] !== exceptId,
    }),
    ...(resource.invalidates ?? []).map((key) => queryCache.invalidateQueries({ key: [key] })),
  ])

type ResourceListOptions = {
  /** Filters, search and scope; a change starts again from page 1. */
  params?: MaybeRefOrGetter<ListQuery>
  pageSize?: MaybeRefOrGetter<number | undefined>
  enabled?: MaybeRefOrGetter<boolean>
}

/** Paginated list as one infinite query under `[key, 'list', params]`; pages are appended by `loadNextPage`. */
export const useResourceList = <TItem extends ResourceItem>(
  resource: MaybeRefOrGetter<Resource<TItem, any, any, any>>,
  options: ResourceListOptions = {},
) => {
  const client = useApiClient()
  const pageSize = () => toValue(options.pageSize) ?? DEFAULT_PAGE_SIZE
  const query = useInfiniteQuery({
    key: () => resourceKeys(toValue(resource)).list({ ...toValue(options.params), page_size: pageSize() }),
    query: ({ pageParam, signal }) =>
      fetchPage(toValue(resource), client, toValue(options.params) ?? {}, pageParam, pageSize(), signal),
    initialPageParam: 1,
    getNextPageParam: (last, _pages, lastPage) => (last.hasNext ? lastPage + 1 : null),
    enabled: () => toValue(options.enabled) ?? true,
  })
  const items = computed<TItem[]>(() => query.data.value?.pages.flatMap((page) => page.items) ?? [])
  return { ...query, items }
}

/** One record under `[key, id]`; disabled for an empty id or `'new'`. */
export const useResourceItem = <TItem extends ResourceItem>(
  resource: MaybeRefOrGetter<Resource<TItem, any, any, any>>,
  id: MaybeRefOrGetter<string | null | undefined>,
) => {
  const client = useApiClient()
  const currentId = () => {
    const value = toValue(id)
    return value && value !== 'new' ? value : null
  }
  return useQuery({
    key: () => resourceKeys(toValue(resource)).detail(currentId() ?? 'new'),
    query: ({ signal }) => fetchItem(toValue(resource), client, currentId()!, signal),
    enabled: () => Boolean(currentId()),
  })
}

/** Save (create or update from a form) and remove; both invalidate the resource's lists on success. */
export const useResourceMutations = <TItem extends ResourceItem, TForm extends ResourceForm, TCreate, TUpdate>(
  resource: MaybeRefOrGetter<Resource<TItem, TForm, TCreate, TUpdate>>,
) => {
  const client = useApiClient()
  const queryCache = useQueryCache()
  const save = useMutation({
    mutation: (form: TForm) => saveItem(toValue(resource), client, form),
    onSuccess: async ({ item }) => {
      const current = toValue(resource)
      queryCache.setQueryData(resourceKeys(current).detail(item.id), item)
      await invalidateResource(queryCache, current, item.id)
    },
  })
  const remove = useMutation({
    mutation: (id: string) => destroyItem(toValue(resource), client, id),
    onSuccess: (_result, id) => invalidateResource(queryCache, toValue(resource), id),
  })
  return { save, remove }
}
