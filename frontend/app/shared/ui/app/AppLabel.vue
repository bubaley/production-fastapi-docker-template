<script setup lang="ts">
import { computed } from 'vue'
import AppDataLabel, { type AppDataLabelSize } from './AppDataLabel.vue'
import type { AppLabelConfig } from './types/label-types'
const props = defineProps<Partial<AppLabelConfig> & {
  config?: AppLabelConfig
  mode?: 'icon' | 'label' | 'both'
  variant?: 'default' | 'soft' | 'outline'
  size?: AppDataLabelSize
}>()
const resolved = computed(() => props.config ?? { label: props.label ?? '', icon: props.icon ?? '', color: props.color, tone: props.tone })
</script>
<template>
  <AppDataLabel
    :config="resolved"
    :size="size"
    :variant="variant"
    :icon-only="mode === 'icon'"
    :hide-icon="mode === 'label'"
  />
</template>
