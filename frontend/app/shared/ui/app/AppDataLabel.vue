<template>
  <div class="app-data-label inline-flex items-start gap-3">
    <slot name="overlay" />
    <AppBlock
      v-if="resolvedIcon"
      :icon="resolvedIcon"
      :color="resolvedColor"
      :size="iconSize"
      variant="ghost"
      square
    />
    <div class="min-w-0">
      <div
        v-if="label || $slots['label-append'] || $slots['label-tooltip']"
        class="flex items-center gap-2"
      >
        <span
          class="fg-secondary"
          :class="labelClass"
        >
          {{ label }}
          <span
            v-if="$slots['label-tooltip']"
            class="ml-1 inline-flex cursor-help align-middle"
          >
            <AppIcon
              icon="lucide:circle-help"
              :size="14"
              color="secondary"
            />
            <AppPopover>
              <div class="max-w-xs p-1 text-sm">
                <slot name="label-tooltip" />
              </div>
            </AppPopover>
          </span>
        </span>
        <slot name="label-append" />
      </div>
      <div :class="valueClass">
        <template v-if="hasValue || $slots.default">
          <AppTextButton
            v-if="hasValue && (to || copied)"
            :to="to"
            :label="displayValue"
            :value="displayValue"
            :copied="copied"
            :weight="valueWeight"
          />
          <template v-else-if="hasValue">{{ displayValue }}</template>
          <slot />
        </template>
        <span
          v-else
          class="fg-tertiary"
        >
          {{ EMPTY_DATA_LABEL }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import { EMPTY_DATA_LABEL, type AppLabelConfig } from '~/shared/ui/app/types/label-types'
import type { ColorToken, SizeToken, WeightToken } from '~/shared/ui/template/types/template-ui-tokens'

export type AppDataLabelSize = 'md' | 'xl'

export type AppDataLabelProps = {
  config?: AppLabelConfig | null
  icon?: string
  label?: string
  value?: unknown
  color?: ColorToken
  size?: AppDataLabelSize
  copied?: boolean
  to?: string | RouteLocationRaw
}

const props = withDefaults(defineProps<AppDataLabelProps>(), {
  size: 'md',
})

const rawValue = computed(() => {
  if (props.value !== undefined && props.value !== null) return props.value
  return props.config?.label ?? null
})

const hasValue = computed(() => rawValue.value !== null && rawValue.value !== '')

const displayValue = computed(() => {
  if (!hasValue.value) return ''
  return String(rawValue.value)
})

const resolvedIcon = computed(() => props.icon || props.config?.icon)
const resolvedColor = computed(() => props.color || props.config?.color)

const iconSize = computed<SizeToken>(() => (props.size === 'xl' ? '2xl' : 'xl'))
const labelClass = computed(() => (props.size === 'md' ? 'text-sm' : undefined))
const valueWeight = computed<WeightToken>(() => (props.size === 'xl' ? 'semibold' : 'medium'))
const valueClass = computed(() => (props.size === 'xl' ? 'text-xl font-semibold' : 'font-medium'))
</script>
