<script setup lang="ts">
import { computed, type Component } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { CircleQuestionMark } from '@lucide/vue'
import { EMPTY_DATA_LABEL, type AppLabelConfig } from './types/label-types'
import { toneVariants, type Tone } from './tone'
import type { AppIconSize } from './AppIcon.vue'

export type AppDataLabelSize = AppIconSize | 'xl'
export type AppDataLabelProps = {
  config?: AppLabelConfig | null
  icon?: Component
  label?: string
  value?: unknown
  tone?: Tone
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
const resolvedTone = computed(() => props.tone || props.config?.tone)
const iconSize = computed(() => (props.size === 'xl' ? 'lg' : props.size))
const compact = computed(() => !props.label)
const textSize = computed(() =>
  props.size === 'xl' ? 'text-xl font-semibold' : props.size === 'xs' ? 'text-xs' : 'text-sm',
)
const toneClasses = computed(() => {
  if (props.variant === 'default') return resolvedTone.value && toneVariants({ tone: resolvedTone.value })
  return toneVariants({ tone: resolvedTone.value ?? 'neutral', appearance: props.variant })
})
</script>
<template>
  <span
    class="inline-flex min-w-0"
    :class="[
      compact ? 'items-center' : 'items-start',
      size === 'xs' ? 'gap-1' : 'gap-2',
      variant !== 'default' && 'rounded-md px-2 py-1',
      variant === 'outline' && 'border',
      toneClasses,
    ]"
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
        <AppTooltip v-if="$slots['label-tooltip']">
          <template #trigger>
            <AppButton
              :icon="CircleQuestionMark"
              size="icon-xs"
              variant="ghost"
              aria-label="Подробнее о поле"
            />
          </template>
          <slot name="label-tooltip" />
        </AppTooltip>
      </span>
      <span :class="[textSize, labelClass, compact && 'truncate', !hasValue && 'text-muted-foreground']">
        <AppTextButton
          v-if="hasValue && (to || copied)"
          :to="to"
          :class="resolvedTone && '!text-inherit'"
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
