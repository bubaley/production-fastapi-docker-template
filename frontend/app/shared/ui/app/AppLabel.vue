<template>
  <FloatLabel :variant="variant">
    <slot />
    <label for="on_label">{{ label }}</label>
  </FloatLabel>
</template>

<script setup lang="ts">
import type { FloatLabelProps } from 'primevue/floatlabel'

export type AppLabelProps = FloatLabelProps & {
  label?: string
  variant?: 'in' | 'on' | 'over'
}
withDefaults(defineProps<AppLabelProps>(), {
  variant: 'on',
})
</script>
