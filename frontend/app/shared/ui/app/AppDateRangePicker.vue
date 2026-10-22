<script setup lang="ts">
import { computed } from 'vue'
import AppButton, { type AppButtonProps } from './AppButton.vue'
import AppDatePicker from './AppDatePicker.vue'
import AppDateRangeLabel from './AppDateRangeLabel.vue'
import type { DatePickerRange } from './date-picker/types'
export type AppDateRange = { from: string | null; to: string | null }
withDefaults(
  defineProps<{
    disabled?: boolean
    locale?: 'ru' | 'en'
    variant?: AppButtonProps['variant']
    size?: AppButtonProps['size']
  }>(),
  {
    locale: 'ru',
    variant: 'ghost',
    size: 'sm'
  }
)
const model = defineModel<AppDateRange>({ default: () => ({ from: null, to: null }) })
const open = defineModel<boolean>('open', { default: false })
defineSlots<{ empty(): unknown }>()
const dates = computed<DatePickerRange>({
  get: () => ({ start: model.value.from, end: model.value.to }),
  set: (value) => {
    model.value = { from: value.start, to: value.end }
  }
})
</script>
<template>
  <AppDatePicker
    v-model:range="dates"
    v-model:open="open"
    mode="range"
    allow-partial
    clearable
    :disabled="disabled"
    :locale="locale"
  >
    <template #trigger>
      <AppButton
        :variant="variant"
        class="w-full justify-start !px-2 text-left"
        :size="size"
        :disabled="disabled"
        :aria-label="locale === 'en' ? 'Change date range' : 'Изменить срок'"
      >
        <AppDateRangeLabel
          v-if="model.from || model.to"
          :start-date="model.from"
          :end-date="model.to"
          type="date"
          :locale="locale"
        />
        <span
          v-else
          class="inline-flex text-muted-foreground"
        ><slot name="empty">{{ locale === 'en' ? 'Not set' : 'Не задан' }}</slot></span>
      </AppButton>
    </template>
  </AppDatePicker>
</template>
