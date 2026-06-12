<template>
  <AppModal
    v-model="model"
    :width="width"
    :title="title"
    :subtitle="hideSubtitle ? undefined : subtitle"
    v-bind="$attrs"
  >
    <slot />
    <div class="mt-6">
      <slot
        v-if="$slots.actions"
        name="actions"
      />
      <div
        v-else
        class="flex gap-3"
      >
        <div class="flex-1">
          <AppButton
            v-bind="{ ...confirmProps, loading: confirmLoading }"
            fluid
            class="flex-1"
            :label="confirmText"
            @click="_handleConfirm"
          />
        </div>
        <div class="flex-1">
          <AppButton
            v-bind="{ ...confirmProps, loading: declineLoading }"
            severity="secondary"
            fluid
            class="flex-1"
            :label="declineText"
            @click="_handleDecline"
          />
        </div>
      </div>
    </div>
  </AppModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppButton, { type AppButtonProps } from './AppButton.vue'
import AppModal, { type AppModalProps } from './AppModal.vue'

const model = defineModel<boolean>()

export interface CConfirmModalProps extends AppModalProps {
  confirmText?: string
  declineText?: string
  confirmProps?: AppButtonProps
  declineProps?: AppButtonProps
  confirm?: () => Promise<void> | void
  decline?: () => Promise<void> | void

  hideSubtitle?: boolean
}
const props = withDefaults(defineProps<CConfirmModalProps>(), {
  width: '25rem',
  confirmText: 'Подтвердить',
  declineText: 'Отмена',
  title: 'Подтверждение действия',
  subtitle: 'Вы уверены, что хотите выполнить это действие?',
  hideSubtitle: false,
})

const confirmLoading = ref(false)
const declineLoading = ref(false)

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

<style lang="scss" scoped></style>
