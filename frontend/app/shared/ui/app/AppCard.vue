<script setup lang="ts">
import { computed } from 'vue'
import { Card } from '~/shared/ui/shadcn/card'
import { cn } from '~/shared/lib/utils'
import { toneVariants, type Tone } from './tone'

export type AppCardProps = {
  variant?: 'default' | 'outline' | 'muted' | 'elevated'
  /** Tints the surface and border with a semantic tone. */
  tone?: Tone
  interactive?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}
const props = withDefaults(defineProps<AppCardProps>(), { variant: 'outline', padding: 'md' })
const variants = {
  default: 'border-transparent',
  outline: '',
  muted: 'border-transparent bg-muted/50 text-foreground',
  elevated: 'shadow-md',
}
const paddings = { none: 'p-0', sm: 'p-3', md: 'p-4', lg: 'p-6' }
// The shadcn card is a flex column with fixed paddings; AppCard is a plain surface with its own spacing scale.
const classes = computed(() =>
  cn(
    'block min-w-0 gap-0 rounded-lg shadow-none',
    variants[props.variant],
    paddings[props.padding],
    props.tone && props.tone !== 'neutral' && toneVariants({ tone: props.tone, appearance: 'tinted' }),
    props.interactive && 'transition-colors focus-within:ring-2 focus-within:ring-ring hover:bg-accent',
  ),
)
</script>
<template>
  <Card :class="classes">
    <slot />
  </Card>
</template>
