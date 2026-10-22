<script setup lang="ts">
import type { Component } from 'vue'
import { Circle, LoaderCircle } from '@lucide/vue'
import { semanticColorClasses, type AppSemanticColor } from './types/label-types'
export type AppIconSize = 'xs' | 'sm' | 'md' | 'lg'
export type AppIconProps = {
  icon?: Component | string
  size?: AppIconSize | number
  label?: string
  color?: AppSemanticColor
  loading?: boolean
}
withDefaults(defineProps<AppIconProps>(), { icon: () => Circle, size: 'md' })
const sizes: Record<AppIconSize, number> = { xs: 12, sm: 14, md: 16, lg: 20 }
</script>
<template>
  <Icon
    v-if="typeof icon === 'string' && !loading"
    :name="icon"
    :size="typeof size === 'number' ? size : sizes[size]"
    class="inline-block shrink-0 align-middle"
    :class="color && semanticColorClasses[color]"
    :aria-label="label"
    :aria-hidden="label ? undefined : true"
  />
  <component
    :is="loading ? LoaderCircle : icon"
    v-else
    :size="typeof size === 'number' ? size : sizes[size]"
    :stroke-width="1.8"
    class="inline-block shrink-0 align-middle"
    :class="[loading && 'animate-spin', color && semanticColorClasses[color]]"
    :role="label ? 'img' : undefined"
    :aria-label="label"
    :aria-hidden="label ? undefined : true"
  />
</template>
