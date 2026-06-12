<template>
  <AppTemplateActions
    :actions="actions"
    :full-width="fullWidth"
    :size="size"
  />
  <AppConfirmModal
    v-model="deleteModal"
    title="Подтверждение удаления"
    subtitle="Уверены, что хотите удалить?"
    :confirm="handleDeleteConfirm"
  />
</template>

<script setup generic="T extends AppModel" lang="ts">
import type { AppTemplateAction } from './types/template-types'
import type { ActionDisplayMode } from './types/template-ui-tokens'

export type AppDetailActionsProps<T extends AppModel> = {
  repo: AppRepoStore<T>
  item: T
  hideCreateButton?: boolean
  hideUpdateButton?: boolean
  hideSaveButton?: boolean
  hideDeleteButton?: boolean
  showCancelButton?: boolean
  hideActions?: boolean
  fullWidth?: boolean
  size?: 'small' | 'large'
  saveMode?: ActionDisplayMode
  deleteMode?: ActionDisplayMode
  disableRouterAutoResolving?: boolean
  beforeSave?: (item: T) => Promise<void> | void
  beforeDelete?: (item: T) => Promise<void> | void
}

const props = withDefaults(defineProps<AppDetailActionsProps<T>>(), {
  fullWidth: false,
  saveMode: 'label',
  deleteMode: 'both',
})

const emit = defineEmits<{
  save: [event: AppDetailActionsSaveResult<T>]
  delete: [event: AppDetailActionsDeleteResult<T>]
  cancel: []
}>()

const deleteModal = ref(false)
const { updateOrCreate, saveLoading, deleteLoading, deleteItem } = useDetailActions(props.repo)

const hideSaveButton = computed(() => {
  if (props.hideSaveButton || props.hideActions) return true
  if (props.hideCreateButton && !props.item.id) return true
  if (props.hideUpdateButton && props.item.id) return true
  return false
})

const actions = computed<AppTemplateAction[]>(() => {
  const values: AppTemplateAction[] = [
    {
      label: 'Сохранить',
      mode: props.saveMode,
      hidden: hideSaveButton.value,
      loading: saveLoading.value,
      action: handleSave,
    },
    {
      label: 'Удалить',
      icon: 'lucide:trash-2',
      severity: 'secondary',
      mode: props.deleteMode,
      hidden: props.hideDeleteButton || props.hideActions || !props.item.id,
      loading: deleteLoading.value,
      action: () => {
        deleteModal.value = true
      },
    },
    {
      label: 'Отмена',
      severity: 'secondary',
      hidden: !props.showCancelButton || props.hideActions,
      action: () => emit('cancel'),
    },
  ]

  return values
})

const handleSave = async () => {
  await props.beforeSave?.(props.item)
  const result = await updateOrCreate(props.item, {
    changeRouteParam: !props.disableRouterAutoResolving,
  })

  if (!result.success) return

  emit('save', result)
}

const handleDeleteConfirm = async () => {
  await props.beforeDelete?.(props.item)
  const result = await deleteItem(props.item)

  if (!result.success) return

  emit('delete', result)
}
</script>
