<script setup lang="ts">
import type { Component } from 'vue'
import { Circle, LoaderCircle } from '@lucide/vue'
import { toneVariants, type Tone } from './tone'
export type AppIconSize = 'xs' | 'sm' | 'md' | 'lg'
export type AppIconProps = {
  /** A Lucide component (`import { House } from '@lucide/vue'`). */
  icon?: Component
  size?: AppIconSize | number
  /** Accessible name; without it the icon is decorative (`aria-hidden`). */
  label?: string
  tone?: Tone
  loading?: boolean
}
withDefaults(defineProps<AppIconProps>(), { icon: () => Circle, size: 'md' })
const sizes: Record<AppIconSize, number> = { xs: 12, sm: 14, md: 16, lg: 20 }
</script>
<template>
  <component
    :is="loading ? LoaderCircle : icon"
    :size="typeof size === 'number' ? size : sizes[size]"
    :stroke-width="1.8"
    class="inline-block shrink-0 align-middle"
    :class="[loading && 'animate-spin', tone && toneVariants({ tone })]"
    :role="label ? 'img' : undefined"
    :aria-label="label"
    :aria-hidden="label ? undefined : true"
  />
</template>
