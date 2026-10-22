import { computed, ref, toValue, watch, type MaybeRefOrGetter, type Ref } from 'vue'
import { deepClone } from '~/shared/lib/clone'
import type { Resource, ResourceForm, ResourceItem } from '~/shared/api/resource'
import { useResourceItem } from '~/shared/api/useResource'

/**
 * The detail form for the record in the route (`:id`, `new` for a new one). The record comes from the
 * `[key, id]` query; the form is a copy taken once per record, so background refetches never overwrite edits.
 */
export function useTemplateDetail<TItem extends ResourceItem, TForm extends ResourceForm>(
  resource: MaybeRefOrGetter<Resource<TItem, TForm, any, any>>,
  detailRouteParam: string,
  buildNewItem?: () => TForm,
  preloadItem = true,
) {
  const route = useRoute()
  const routeId = computed(() => String(route.params[detailRouteParam] ?? ''))
  const isNew = computed(() => !routeId.value || routeId.value === 'new')
  const query = useResourceItem(resource, () => (preloadItem && !isNew.value ? routeId.value : null))
  const item = ref(null) as Ref<TForm | null>
  let formFor: string | null = null

  const sync = () => {
    if (!preloadItem) return
    if (isNew.value) {
      if (formFor === 'new') return
      formFor = 'new'
      item.value = buildNewItem?.() ?? toValue(resource).toForm()
      return
    }
    if (formFor === routeId.value) return
    const data = query.data.value
    if (data && data.id === routeId.value) {
      formFor = data.id
      item.value = toValue(resource).toForm(deepClone(data))
    } else {
      item.value = null
    }
  }
  watch([routeId, () => query.data.value], sync, { immediate: true })

  /** After a save: show the saved record without waiting for a refetch. */
  const setItem = (form: TForm) => {
    formFor = form.id || 'new'
    item.value = form
  }

  return {
    item,
    loading: computed(() => query.isLoading.value),
    error: computed(() => query.error.value),
    loadItem: () => query.refetch(),
    setItem,
  }
}
