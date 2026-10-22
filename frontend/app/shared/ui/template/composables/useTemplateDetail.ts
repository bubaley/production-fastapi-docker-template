import { computed, onMounted, onScopeDispose, ref, shallowRef, watch } from 'vue'

export const useTemplateDetail = <T extends AppModel>(
  repo: AppRepoStore<T>,
  detailRouteParam: string,
  buildNewItem?: () => T,
  preloadItem = true,
) => {
  const route = useRoute()
  const loading = ref(false)
  const error = shallowRef<Error | null>(null)
  const item = ref<T | null>(null) as Ref<T | null>
  let generation = 0
  const routeItemId = computed(() => String(route.params[detailRouteParam] ?? ''))
  const invalidate = () => {
    generation++
    item.value = null
    error.value = null
    loading.value = false
  }
  const loadItem = async () => {
    invalidate()
    const request = generation
    loading.value = true
    try {
      let result: T | undefined
      if (!routeItemId.value || routeItemId.value === 'new') {
        if (!buildNewItem) throw new Error('Не удалось создать запись')
        result = buildNewItem()
      } else {
        result = await repo.retrieve(routeItemId.value, undefined, undefined, { storeInRepo: false })
      }
      if (request !== generation) return
      if (!result) throw new Error('Не удалось загрузить запись')
      item.value = result
    } catch (reason) {
      if (request === generation) error.value = reason instanceof Error ? reason : new Error(String(reason))
    } finally {
      if (request === generation) loading.value = false
    }
  }
  onMounted(() => { if (preloadItem) void loadItem() })
  watch(routeItemId, () => {
    invalidate()
    if (preloadItem) void loadItem()
  }, { flush: 'sync' })
  watch(() => repo.revision, invalidate, { flush: 'sync' })
  onScopeDispose(invalidate)
  return { loadItem, item, loading, error }
}
