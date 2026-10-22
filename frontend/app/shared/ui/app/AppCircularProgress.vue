<script setup lang="ts">
import { computed } from 'vue'
import { toneVariants, type Tone } from './tone'
const props = withDefaults(
  defineProps<{
    value?: number
    min?: number
    max?: number
    size?: string | number
    thickness?: number
    tone?: Tone
    showValue?: boolean
  }>(),
  { value: 0, min: 0, max: 100, size: 40, thickness: 0.16, showValue: true },
)
const normalized = computed(() => {
  const range = props.max - props.min
  return Number.isFinite(props.value) && range > 0
    ? Math.max(0, Math.min(100, ((props.value - props.min) / range) * 100))
    : 0
})
const size = computed(() => (typeof props.size === 'number' ? `${props.size}px` : props.size))
const stroke = computed(() => Math.max(1, Math.min(20, props.thickness * 40)))
</script>
<template>
  <span
    class="relative inline-grid shrink-0 place-items-center align-middle"
    :style="{ width: size, height: size }"
    role="progressbar"
    :aria-valuenow="normalized"
    :aria-valuemin="0"
    :aria-valuemax="100"
  >
    <svg
      viewBox="0 0 40 40"
      class="absolute inset-0 size-full -rotate-90"
      aria-hidden="true"
      fill="none"
    >
      <circle
        cx="20"
        cy="20"
        :r="20 - stroke / 2"
        :stroke-width="stroke"
        class="stroke-border"
      />
      <circle
        cx="20"
        cy="20"
        :r="20 - stroke / 2"
        :stroke-width="stroke"
        :class="toneVariants({ tone: tone ?? 'primary', appearance: 'stroke' })"
        pathLength="100"
        :stroke-dasharray="`${normalized} 100`"
      />
    </svg>
    <span
      v-if="showValue"
      class="relative"
      ><slot>{{ Math.round(normalized) }}%</slot></span
    >
  </span>
</template>
