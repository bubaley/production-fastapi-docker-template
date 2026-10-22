export type AppDetailActionsConfig = {
  successMessage?: string
  errorMessage?: string
  disableNotification?: boolean
  changeRouteParam?: boolean
}

export const useDetailActions = <T extends AppModel>(repo: AppRepoStore<T>) => {
  const toast = useToast()

  const saveLoading = ref(false)
  const route = useRoute()
  const router = useRouter()
  const deleteLoading = ref(false)
  const _items = toRef(repo, 'items')

  const { updateListItem, deleteListItem } = useListEvents({
    items: _items,
    key: 'id',
  })

  const _handleError = (error: any, summary: string, config?: AppDetailActionsConfig) => {
    if (!config?.disableNotification) {
      toast.error(summary)
    }
    console.error({
      error: error?.toString(),
      data: error?.response?.data,
    })
  }

  const updateOrCreate = async (item: T, config?: AppDetailActionsConfig): Promise<AppDetailActionsSaveResult<T>> => {
    let result: T | undefined
    let created = false
    let success = true

    try {
      saveLoading.value = true
      if (item.id) {
        result = await repo.update(item)
      } else {
        result = await repo.create(item)
        created = true
        if (config?.changeRouteParam && result) changeRouteParam(result)
      }
      if (!result) throw new Error('Сервер не вернул сохранённую запись')
      updateListItem(result)
      if (!config?.disableNotification) {
        toast.default(config?.successMessage || 'Сохранено')
      }
    } catch (error: any) {
      _handleError(error, config?.errorMessage || 'Ошибка сохранения', config)
      success = false
    } finally {
      saveLoading.value = false
    }
    return {
      item: result,
      created,
      success,
    }
  }

  const changeRouteParam = (item: T) => {
    const routeKey = Object.keys(route.params).at(-1)
    if (routeKey && item?.id) {
      void router.replace({
        name: route.name,
        params: { ...route.params, [routeKey]: item.id },
      })
    }
  }

  const deleteItem = async (item: T, config?: AppDetailActionsConfig): Promise<AppDetailActionsDeleteResult<T>> => {
    let success = true
    try {
      deleteLoading.value = true
      await repo.delete(item)
      deleteListItem(item)
      if (!config?.disableNotification) toast.default(config?.successMessage || 'Удалено')
    } catch (error) {
      _handleError(error, config?.errorMessage || 'Ошибка удаления', config)
      success = false
    } finally {
      deleteLoading.value = false
    }
    return { success, item }
  }

  return {
    updateOrCreate,
    deleteItem,
    changeRouteParam,
    saveLoading,
    deleteLoading,
  }
}
