import type { MaybeRefOrGetter } from 'vue'
import { computed, toValue } from 'vue'
import type { Resource, ResourceForm, ResourceItem } from '~/shared/api/resource'
import { useResourceMutations } from '~/shared/api/useResource'

export type AppDetailActionsConfig = {
  successMessage?: string
  errorMessage?: string
  disableNotification?: boolean
  changeRouteParam?: boolean
}

/** Save/delete for a detail form through the resource mutations (lists refresh by invalidation). */
export function useDetailActions<TItem extends ResourceItem, TForm extends ResourceForm>(
  resource: MaybeRefOrGetter<Resource<TItem, TForm, any, any>>,
) {
  const toast = useToast()
  const route = useRoute()
  const router = useRouter()
  const { save, remove } = useResourceMutations(resource)

  const notifyError = (error: unknown, summary: string, config?: AppDetailActionsConfig) => {
    if (!config?.disableNotification) toast.error(summary)
    console.error(error)
  }

  const changeRouteParam = (item: { id: string }) => {
    const routeKey = Object.keys(route.params).at(-1)
    if (routeKey && item.id) {
      void router.replace({
        name: route.name,
        params: { ...route.params, [routeKey]: item.id },
      })
    }
  }

  const updateOrCreate = async (
    form: TForm,
    config?: AppDetailActionsConfig,
  ): Promise<AppDetailActionsSaveResult<TForm, TItem>> => {
    try {
      const { item, created } = await save.mutateAsync(form)
      if (created && config?.changeRouteParam) changeRouteParam(item)
      if (!config?.disableNotification) toast.default(config?.successMessage || 'Сохранено')
      return { item: toValue(resource).toForm(item), saved: item, created, success: true }
    } catch (error) {
      notifyError(error, config?.errorMessage || 'Ошибка сохранения', config)
      return { item: undefined, created: false, success: false }
    }
  }

  const deleteItem = async (
    form: TForm,
    config?: AppDetailActionsConfig,
  ): Promise<AppDetailActionsDeleteResult<TForm>> => {
    try {
      if (!form.id) throw new Error('Запись ещё не сохранена')
      await remove.mutateAsync(form.id)
      if (!config?.disableNotification) toast.default(config?.successMessage || 'Удалено')
      return { success: true, item: form }
    } catch (error) {
      notifyError(error, config?.errorMessage || 'Ошибка удаления', config)
      return { success: false, item: form }
    }
  }

  return {
    updateOrCreate,
    deleteItem,
    changeRouteParam,
    saveLoading: computed(() => save.isLoading.value),
    deleteLoading: computed(() => remove.isLoading.value),
  }
}
