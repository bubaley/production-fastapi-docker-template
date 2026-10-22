<script setup lang="ts">
import { computed } from 'vue'
import { semanticColorVariables } from './types/label-types'
export type AppCardProps = {
  variant?: 'default' | 'outlined' | 'muted' | 'elevated'
  color?: 'neutral' | 'primary' | 'success' | 'info' | 'warning' | 'danger' | 'destructive'
  outlined?: boolean
  elevated?: boolean
  interactive?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
  as?: 'article' | 'div' | 'section'
}
const props = withDefaults(defineProps<AppCardProps>(), {
  variant: 'outlined',
  padding: 'md',
  as: 'div',
  color: 'neutral',
})
const variants = {
  default: 'bg-card text-card-foreground',
  outlined: 'border border-border bg-card text-card-foreground',
  muted: 'bg-muted/50 text-foreground',
  elevated: 'border border-border bg-card text-card-foreground shadow-md',
}
const colorStyle = computed(() =>
  props.color === 'neutral'
    ? undefined
    : {
        backgroundColor: `color-mix(in srgb, ${semanticColorVariables[props.color]} 10%, var(--card))`,
        borderColor: `color-mix(in srgb, ${semanticColorVariables[props.color]} 45%, var(--card))`,
      },
)
const paddings = { none: '', sm: 'p-3', md: 'p-4', lg: 'p-6' }
</script>
<template>
  <component
    :is="as"
    :style="colorStyle"
    :class="[
      'min-w-0 rounded-lg',
      variants[variant],
      paddings[padding],
      outlined && 'border border-border',
      elevated && 'shadow-md',
      interactive && 'transition-colors focus-within:ring-2 focus-within:ring-ring hover:bg-accent',
    ]"
  >
    <slot />
  </component>
</template>
