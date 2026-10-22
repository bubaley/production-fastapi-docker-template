<template>
  <AppTemplateActions
    v-bind="$attrs"
    :actions="actions"
    :full-width="fullWidth"
    :size="size"
  />
  <AppConfirmModal
    v-model="deleteModal"
    :title="labels?.deleteTitle || 'Подтверждение удаления'"
    :confirm-text="labels?.delete || 'Удалить'"
    :decline-text="labels?.cancel"
    :close-label="labels?.close"
    :confirm-props="{ variant: 'destructive' }"
    :subtitle="labels?.deleteDescription || 'Уверены, что хотите удалить?'"
    :confirm="handleDeleteConfirm"
  />
</template>

<script setup generic="T extends ResourceItem, F extends ResourceForm" lang="ts">
import type { Resource, ResourceForm, ResourceItem } from '~/shared/api/resource'
import type { AppTemplateAction } from './types/template-types'
import type { ActionDisplayMode } from './types/template-ui-tokens'
import type { AppButtonSize } from '../app/types/control'
import { Trash2 } from '@lucide/vue'

export type AppDetailActionsProps<T extends ResourceItem, F extends ResourceForm> = {
  labels?: {
    save?: string
    cancel?: string
    delete?: string
    deleteTitle?: string
    deleteDescription?: string
    close?: string
    saved?: string
    deleted?: string
    saveError?: string
    deleteError?: string
  }
  resource: Resource<T, F, any, any>
  item: F
  hideCreateButton?: boolean
  hideUpdateButton?: boolean
  hideSaveButton?: boolean
  hideDeleteButton?: boolean
  showCancelButton?: boolean
  hideActions?: boolean
  hideHeaderActions?: boolean
  hidden?: boolean
  fullWidth?: boolean
  size?: AppButtonSize
  saveMode?: ActionDisplayMode
  deleteMode?: ActionDisplayMode
  disableRouterAutoResolving?: boolean
  reverseActions?: boolean
  beforeSave?: (item: F) => Promise<void> | void
  beforeDelete?: (item: F) => Promise<void> | void
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<AppDetailActionsProps<T, F>>(), {
  fullWidth: false,
  saveMode: 'label',
  deleteMode: 'both',
})

const emit = defineEmits<{
  save: [event: AppDetailActionsSaveResult<F, T>]
  delete: [event: AppDetailActionsDeleteResult<F>]
  cancel: []
}>()

const deleteModal = ref(false)
const { updateOrCreate, saveLoading, deleteLoading, deleteItem } = useDetailActions(() => props.resource)

const hideSaveButton = computed(() => {
  if (props.hideSaveButton || props.hideActions) return true
  if (props.hideCreateButton && !props.item.id) return true
  if (props.hideUpdateButton && props.item.id) return true
  return false
})

const actions = computed<AppTemplateAction[]>(() => {
  const values: AppTemplateAction[] = [
    {
      label: props.labels?.cancel || 'Отмена',
      variant: 'secondary',
      hidden: !props.showCancelButton || props.hideActions,
      action: () => emit('cancel'),
    },
    {
      label: props.labels?.delete || 'Удалить',
      icon: Trash2,
      variant: 'secondary',
      mode: props.deleteMode,
      hidden: props.hideDeleteButton || props.hideActions || !props.item.id,
      loading: deleteLoading.value,
      action: () => {
        deleteModal.value = true
      },
    },

    {
      label: props.labels?.save || 'Сохранить',
      mode: props.saveMode,
      hidden: hideSaveButton.value,
      loading: saveLoading.value,
      action: handleSave,
    },
  ]

  if (props.reverseActions) {
    values.reverse()
  }

  return values
})

const handleSave = async () => {
  await props.beforeSave?.(props.item)
  const result = await updateOrCreate(props.item, {
    changeRouteParam: !props.disableRouterAutoResolving,
    successMessage: props.labels?.saved,
    errorMessage: props.labels?.saveError,
  })

  if (!result.success) return

  emit('save', result)
}

const handleDeleteConfirm = async () => {
  await props.beforeDelete?.(props.item)
  const result = await deleteItem(props.item, {
    successMessage: props.labels?.deleted,
    errorMessage: props.labels?.deleteError,
  })

  if (!result.success) throw new Error('Удаление не выполнено')

  emit('delete', result)
}
</script>
