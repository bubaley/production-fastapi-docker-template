<script setup lang="ts">
import { computed } from 'vue'
import AppButton from './AppButton.vue'
import AppDatePicker from './AppDatePicker.vue'
import type { DatePickerRange } from './date-picker/types'
const model = defineModel<string[]>()
withDefaults(defineProps<{ clearable?: boolean; locale?: 'ru' | 'en' }>(), { locale: 'ru' })
const dates = computed<DatePickerRange>({
  get: () => ({ start: model.value?.[0] || null, end: model.value?.[1] || null }),
  set: (value) => {
    model.value = value.start || value.end ? [value.start || '', value.end || ''] : undefined
  }
})
</script>
<template>
  <AppDatePicker
    v-model:range="dates"
    mode="range"
    apply-mode="manual"
    allow-partial
    :clearable="clearable"
    :locale="locale"
  >
    <template #trigger="{ formattedValue }">
      <AppButton
        variant="outline"
        size="sm"
      >
        <slot />{{ formattedValue }}
      </AppButton>
    </template>
  </AppDatePicker>
</template>
