import { last } from 'lodash-es'
import { useTemplateListEvents } from './useTemplateListEvents'

export type AppDetailActionsConfig = {
  disableNotification?: boolean
  changeRouteParam?: boolean
}

export const useDetailActions = <T extends AppModel>(repo: AppRepoStore<T>) => {
  const { notify } = useNotify()

  const saveLoading = ref(false)
  const route = useRoute()
  const router = useRouter()
  const deleteLoading = ref(false)
  const _items = toRef(repo, 'items')

  const { updateListItem, deleteListItem } = useTemplateListEvents({
    items: _items,
    key: 'id',
  })

  const _handleError = (error: any, summary: string, config?: AppDetailActionsConfig) => {
    if (!config?.disableNotification) {
      notify({ severity: 'error', summary: summary })
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
      updateListItem(result)
      if (!config?.disableNotification) {
        notify({ summary: 'Сохранено' })
      }
    } catch (error: any) {
      _handleError(error, 'Ошибка сохранения', config)
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
    const routeKey = last(Object.keys(route.params))
    if (routeKey && item?.id) {
      void router.replace({
        name: route.name,
        params: { ...route.params, [routeKey]: item.id },
      })
    }
  }

  const deleteItem = async (item: T): Promise<AppDetailActionsDeleteResult<T>> => {
    let success = true
    try {
      deleteLoading.value = true
      await repo.delete(item)
      deleteListItem(item)
      notify({ summary: 'Удалено' })
    } catch (error) {
      _handleError(error, 'Ошибка удаления')
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
