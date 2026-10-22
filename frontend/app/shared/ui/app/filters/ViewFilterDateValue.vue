<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '../AppButton.vue'
import AppDatePicker from '../AppDatePicker.vue'
import type { AppControlSize } from '../types/control'
import type { DatePickerRange } from '~/shared/ui/app/date-picker/types'
import type { FilterValue, ViewFilterField } from './types'
import { dateFilterValue } from './filterConditions'
const props = withDefaults(
  defineProps<{
    field: ViewFilterField
    lookup: string
    modelValue: FilterValue
    inline?: boolean
    size?: AppControlSize
    locale?: 'ru' | 'en'
    disabled?: boolean
  }>(),
  { size: 'default', locale: 'ru' },
)
const emit = defineEmits<{ 'update:modelValue': [value: FilterValue] }>()
const range = computed<DatePickerRange>(() => ({
  start: Array.isArray(props.modelValue) ? String(props.modelValue[0] || '') || null : null,
  end: Array.isArray(props.modelValue) ? String(props.modelValue[1] || '') || null : null,
}))
function updateRange(value: DatePickerRange) {
  emit('update:modelValue', [
    dateFilterValue(value.start, props.field.kind === 'datetime', false),
    dateFilterValue(value.end, props.field.kind === 'datetime', true),
  ])
}
</script>
<template>
  <AppDatePicker
    class="min-w-0"
    :model-value="lookup === 'range' ? null : String(modelValue || '') || null"
    :range="range"
    :mode="lookup === 'range' ? 'range' : 'single'"
    :time="field.kind === 'datetime'"
    :mask="field.kind === 'datetime' ? 'DD.MM.YYYY HH:mm:ss' : 'DD.MM.YYYY'"
    smart
    allow-partial
    apply-mode="close"
    :clearable="false"
    :disabled="disabled"
    :locale="locale"
    @update:range="updateRange"
    @update:model-value="
      emit(
        'update:modelValue',
        dateFilterValue(
          typeof $event === 'string' ? $event : null,
          field.kind === 'datetime',
          lookup === 'lte' || lookup === 'lt',
        ),
      )
    "
  >
    <template #trigger="{ formattedValue }">
      <AppButton
        :size="size"
        :variant="inline ? 'ghost' : 'outline'"
        :disabled="disabled"
        :aria-label="field.label"
        class="max-w-full truncate"
        :class="formattedValue ? 'text-foreground' : 'text-muted-foreground'"
      >
        <span class="truncate">{{ formattedValue || (locale === 'en' ? 'Select date...' : 'Выбрать дату...') }}</span>
      </AppButton>
    </template>
  </AppDatePicker>
</template>
