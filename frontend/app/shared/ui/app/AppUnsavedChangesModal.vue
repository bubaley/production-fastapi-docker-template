<script setup lang="ts">
import AppModal from './AppModal.vue'
import AppButton from './AppButton.vue'
const model = defineModel<boolean>({ default: false })
withDefaults(
  defineProps<{
    loading?: boolean
    title?: string
    description?: string
    cancelLabel?: string
    discardLabel?: string
    saveLabel?: string
    closeLabel?: string
  }>(),
  {
    title: 'Сохранить изменения?',
    description: 'У вас есть несохранённые изменения.',
    cancelLabel: 'Отмена',
    discardLabel: 'Не сохранять',
    saveLabel: 'Сохранить',
  },
)
const emit = defineEmits<{ save: []; discard: []; cancel: [] }>()
function cancel() {
  model.value = false
  emit('cancel')
}
</script>
<template>
  <AppModal
    v-model="model"
    :title="title"
    :description="description"
    :close-label="closeLabel"
    :prevent-outside-close="loading"
    :escape-disabled="loading"
  >
    <template #footer>
      <AppButton
        variant="secondary"
        :label="cancelLabel"
        :disabled="loading"
        @click="cancel"
      />
      <AppButton
        variant="ghost"
        :label="discardLabel"
        :disabled="loading"
        @click="emit('discard')"
      />
      <AppButton
        :label="saveLabel"
        :loading="loading"
        @click="emit('save')"
      />
    </template>
  </AppModal>
</template>
