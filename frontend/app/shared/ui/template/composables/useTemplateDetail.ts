export const useTemplateDetail = <T extends AppModel>(
  repo: AppRepoStore<T>,
  detailRouteParam: string,
  buildNewItem?: () => T,
  preloadItem = true,
) => {
  const route = useRoute()
  const { restoreRepoItem } = useAppTemplate()
  const loading = ref(false)

  const routeItemId = computed(() => String(route.params[detailRouteParam] ?? ''))

  const item = computed(() => {
    if (!repo.item) return null
    if (!repo.item.id) return repo.item
    const allowedIds = [String(repo.item.id), 'new']
    return allowedIds.includes(routeItemId.value) ? repo.item : null
  })

  const loadItem = async () => {
    loading.value = true
    try {
      await restoreRepoItem({
        repo,
        itemId: routeItemId.value,
        buildNewItem,
      })
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    if (preloadItem) void loadItem()
  })

  watch(routeItemId, () => {
    if (preloadItem) void loadItem()
  })

  return {
    loadItem,
    item,
    loading,
  }
}
