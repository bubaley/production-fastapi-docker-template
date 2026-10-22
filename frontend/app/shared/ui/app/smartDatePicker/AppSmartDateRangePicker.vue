<script setup lang="ts">
import { computed } from 'vue'
import AppDatePicker from '../AppDatePicker.vue'
import type { DatePickerRange } from '../date-picker/types'
import type { SmartDateRange } from './composables/useSmartDateRange'
const model = defineModel<SmartDateRange>({ default: () => ({ from: 'now-1h', to: 'now' }) })
const range = computed({ get: () => ({ start: model.value.from, end: model.value.to }), set: (value: DatePickerRange) => { model.value = { from: value.start ?? '', to: value.end ?? '' } } })
</script>
<template>
  <AppDatePicker
    v-model:range="range"
    mode="range"
    smart
    time
    apply-mode="manual"
  />
</template>
