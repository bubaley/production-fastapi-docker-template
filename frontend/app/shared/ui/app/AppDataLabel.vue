<script setup lang="ts">
import { computed, type Component } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import {
  EMPTY_DATA_LABEL,
  semanticColorClasses,
  semanticColorVariables,
  type AppLabelConfig,
  type AppSemanticColor,
} from './types/label-types'
import type { AppIconSize } from './AppIcon.vue'

export type AppDataLabelSize = AppIconSize | 'xl'
export type AppDataLabelProps = {
  config?: AppLabelConfig | null
  icon?: string | Component
  label?: string
  value?: unknown
  color?: AppSemanticColor
  size?: AppDataLabelSize
  variant?: 'default' | 'soft' | 'outline'
  iconOnly?: boolean
  hideIcon?: boolean
  labelClass?: string
  copied?: boolean
  to?: string | RouteLocationRaw
}
const props = withDefaults(defineProps<AppDataLabelProps>(), { size: 'md', variant: 'default' })
const rawValue = computed(() => props.value ?? props.config?.label ?? null)
const hasValue = computed(() => rawValue.value !== null && rawValue.value !== '')
const displayValue = computed(() => (hasValue.value ? String(rawValue.value) : EMPTY_DATA_LABEL))
const resolvedIcon = computed(() => props.icon || props.config?.icon)
const resolvedColor = computed(() => props.color || props.config?.tone || props.config?.color)
const surfaceStyle = computed(() => {
  const color = resolvedColor.value && semanticColorVariables[resolvedColor.value]
  if (!color) return undefined
  return props.variant === 'soft'
    ? { backgroundColor: `color-mix(in srgb, ${color} 12%, transparent)` }
    : props.variant === 'outline'
      ? { borderColor: `color-mix(in srgb, ${color} 45%, transparent)` }
      : undefined
})
const iconSize = computed(() => (props.size === 'xl' ? 'lg' : props.size))
const compact = computed(() => !props.label)
const textSize = computed(() =>
  props.size === 'xl' ? 'text-xl font-semibold' : props.size === 'xs' ? 'text-xs' : 'text-sm',
)
</script>
<template>
  <span
    class="inline-flex min-w-0"
    :class="[
      compact ? 'items-center' : 'items-start',
      size === 'xs' ? 'gap-1' : 'gap-2',
      variant !== 'default' && 'rounded-md px-2 py-1',
      variant === 'soft' && 'bg-muted/60',
      variant === 'outline' && 'border border-border',
      resolvedColor && semanticColorClasses[resolvedColor],
    ]"
    :style="surfaceStyle"
    :title="iconOnly ? displayValue : undefined"
  >
    <slot name="overlay" />
    <slot
      v-if="!hideIcon"
      name="icon"
    >
      <AppIcon
        v-if="resolvedIcon"
        :icon="resolvedIcon"
        :color="resolvedColor"
        :size="iconSize"
        :class="!compact && 'mt-0.5'"
      />
    </slot>
    <span :class="['min-w-0', iconOnly && 'sr-only']">
      <span
        v-if="label || $slots['label-append'] || $slots['label-tooltip']"
        class="mb-0.5 flex items-center gap-2 text-xs text-muted-foreground"
      >
        {{ label }}
        <slot name="label-append" />
        <AppMenu v-if="$slots['label-tooltip']">
          <template #trigger
            ><AppButton
              icon="lucide:circle-help"
              size="icon-xs"
              variant="ghost"
              aria-label="Подробнее о поле"
          /></template>
          <div class="max-w-xs px-2 py-1.5 text-sm"><slot name="label-tooltip" /></div>
        </AppMenu>
      </span>
      <span :class="[textSize, labelClass, compact && 'truncate', !hasValue && 'text-muted-foreground']">
        <AppTextButton
          v-if="hasValue && (to || copied)"
          :to="to"
          :class="resolvedColor && '!text-inherit'"
          :label="displayValue"
          :value="displayValue"
          :copied="copied"
          :weight="size === 'xl' ? 'semibold' : 'medium'"
        />
        <template v-else-if="hasValue">{{ displayValue }}</template>
        <template v-else-if="!$slots.default">{{ EMPTY_DATA_LABEL }}</template>
        <slot />
      </span>
    </span>
  </span>
</template>
