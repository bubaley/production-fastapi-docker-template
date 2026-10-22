<template>
  <AppButton
    :icon="ChevronLeft"
    variant="ghost"
    size="icon"
    :aria-label="label"
    :title="label"
    @click="backAction"
  />
</template>

<script setup lang="ts">
import { ChevronLeft } from '@lucide/vue'

export type AppBackButtonProps = {
  backAction?: () => void
  label?: string
}

withDefaults(defineProps<AppBackButtonProps>(), { label: 'Назад' })
</script>
