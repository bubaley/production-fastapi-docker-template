<script setup lang="ts">
import { X } from '@lucide/vue'
import AppIcon from './AppIcon.vue'
import { appControlIconSize, type AppControlSize } from './types/control'
withDefaults(defineProps<{ active?: boolean; label: string; size?: AppControlSize }>(), {
  active: false,
  size: 'default'
})
</script>
<template>
  <button
    type="button"
    :style="{
      width: size === 'xs' ? '16px' : size === 'sm' ? '20px' : '24px',
      height: size === 'xs' ? '16px' : size === 'sm' ? '20px' : '24px'
    }"
    :aria-label="label"
    class="z-10 grid size-6 shrink-0 place-items-center rounded-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    :class="
      active
        ? 'text-primary bg-[color-mix(in_srgb,var(--color-primary)_10%,var(--color-background))] group-hover/select:bg-[color-mix(in_srgb,var(--color-primary)_20%,var(--color-background))] group-hover/input:bg-[color-mix(in_srgb,var(--color-primary)_20%,var(--color-background))] hover:!bg-[color-mix(in_srgb,var(--color-primary)_30%,var(--color-background))]'
        : 'bg-background text-muted-foreground group-hover/select:bg-[color:var(--ds-field-hover)] group-hover/input:bg-[color:var(--ds-field-hover)] hover:!bg-accent hover:text-foreground'
    "
  >
    <AppIcon
      :icon="X"
      :size="appControlIconSize[size]"
    />
  </button>
</template>
