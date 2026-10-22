<script setup lang="ts">
import { computed } from 'vue'
import AppInput from './AppInput.vue'
const props = defineProps<{
  modelValue?: number | null
  min?: number
  max?: number
  step?: number | string
  label?: string
  disabled?: boolean
  error?: string
  hint?: string
}>()
const emit = defineEmits<{ 'update:modelValue': [value: number | null] }>()
const text = computed({
  get: () => (props.modelValue == null ? '' : String(props.modelValue)),
  set: (value: string) => {
    const number = value === '' ? null : Number(value)
    if (number === null || Number.isFinite(number)) emit('update:modelValue', number)
  }
})
</script>
<template>
  <AppInput
    v-model="text"
    type="number"
    :label="label"
    :min="min"
    :max="max"
    :step="step"
    :disabled="disabled"
    :error="error"
    :hint="hint"
  />
</template>
