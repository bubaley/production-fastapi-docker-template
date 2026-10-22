<template>
  <AppModal
    v-model="model"
    :width="width"
    :title="title"
    :description="hideSubtitle ? undefined : description || subtitle"
    v-bind="$attrs"
  >
    <slot />
    <template #footer>
      <slot
        v-if="$slots.actions"
        name="actions"
      />
      <div
        v-else
        class="flex gap-3"
      >
        <AppTemplateActions
          :actions="actions"
          full-width
        />
      </div>
    </template>
  </AppModal>
</template>

<script setup lang="ts">
import type { AppButtonProps } from './AppButton.vue'
import AppModal, { type AppModalProps } from './AppModal.vue'
import type { AppTemplateAction } from '../template/types/template-types'

const model = defineModel<boolean>()

export interface AppConfirmModalProps extends AppModalProps {
  confirmText?: string
  declineText?: string
  confirmProps?: AppButtonProps
  declineProps?: AppButtonProps
  confirm?: () => Promise<void> | void
  decline?: () => Promise<void> | void

  hideSubtitle?: boolean
}
const props = withDefaults(defineProps<AppConfirmModalProps>(), {
  width: '25rem',
  confirmText: 'Подтвердить',
  declineText: 'Отмена',
  title: 'Подтверждение действия',
  subtitle: 'Вы уверены, что хотите выполнить это действие?',
  hideSubtitle: false,
})

const confirmLoading = ref(false)
const declineLoading = ref(false)

const actions = computed<AppTemplateAction[]>(() => {
  const declineAction: AppTemplateAction = {
    variant: 'secondary',
    ...props.declineProps,
    fluid: true,
    label: props.declineText,
    loading: declineLoading.value,
    action: _handleDecline,
  }
  const confirmAction: AppTemplateAction = {
    ...props.confirmProps,
    fluid: true,
    label: props.confirmText,
    loading: confirmLoading.value,
    action: _handleConfirm,
  }

  return [declineAction, confirmAction]
})

const _handleDecline = async () => {
  declineLoading.value = true
  try {
    await props.decline?.()
    model.value = false
  } catch (error) {
    console.error(error)
  } finally {
    declineLoading.value = false
  }
}

const _handleConfirm = async () => {
  confirmLoading.value = true
  try {
    await props.confirm?.()
    model.value = false
  } catch (error) {
    console.error(error)
  } finally {
    confirmLoading.value = false
  }
}
</script>
