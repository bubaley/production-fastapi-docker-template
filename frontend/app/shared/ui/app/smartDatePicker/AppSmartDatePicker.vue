<script setup lang="ts">
import AppDatePicker from '../AppDatePicker.vue'
defineProps<{ label?: string; placeholder?: string; showQuickDates?: boolean }>()
const model = defineModel<string | null>({ default: null })
</script>
<template>
  <AppDatePicker
    v-model="model"
    :label="label"
    :placeholder="placeholder"
    :smart="showQuickDates !== false"
    time
  />
</template>
