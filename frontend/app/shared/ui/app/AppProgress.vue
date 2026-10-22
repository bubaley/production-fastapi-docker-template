<script setup lang="ts">
import { Progress } from '~/shared/ui/shadcn/progress'
import type { Tone } from './tone'

withDefaults(
  defineProps<{
    value?: number | null
    max?: number
    tone?: Extract<Tone, 'primary' | 'success' | 'info' | 'warning' | 'destructive'>
    ariaLabel?: string
  }>(),
  { value: 0, max: 100, tone: 'primary' },
)
// Literal class names per tone so Tailwind keeps them.
const indicator = {
  primary: '[&>[data-slot=progress-indicator]]:bg-primary',
  success: '[&>[data-slot=progress-indicator]]:bg-success',
  info: '[&>[data-slot=progress-indicator]]:bg-info',
  warning: '[&>[data-slot=progress-indicator]]:bg-warning',
  destructive: '[&>[data-slot=progress-indicator]]:bg-destructive',
}
</script>

<template>
  <Progress
    :model-value="value"
    :max="max"
    :aria-label="ariaLabel"
    class="bg-muted"
    :class="indicator[tone]"
  />
</template>
