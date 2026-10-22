<script setup lang="ts">
import { X } from '@lucide/vue'
import AppIcon from './AppIcon.vue'
import { appControlIconSize, type AppControlSize } from './types/control'
withDefaults(defineProps<{ active?: boolean; label: string; size?: AppControlSize }>(), {
  active: false,
  size: 'md',
})
</script>
<template>
  <button
    type="button"
    :aria-label="label"
    class="z-10 grid shrink-0 place-items-center rounded-sm transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
    :class="[
      size === 'xs' ? 'size-4' : size === 'sm' ? 'size-5' : 'size-6',
      active
        ? 'bg-[color-mix(in_srgb,var(--color-primary)_10%,var(--color-background))] text-primary group-hover/input:bg-[color-mix(in_srgb,var(--color-primary)_20%,var(--color-background))] group-hover/select:bg-[color-mix(in_srgb,var(--color-primary)_20%,var(--color-background))] hover:!bg-[color-mix(in_srgb,var(--color-primary)_30%,var(--color-background))]'
        : 'bg-background text-muted-foreground group-hover/input:bg-field-hover group-hover/select:bg-field-hover hover:!bg-accent hover:text-foreground',
    ]"
  >
    <AppIcon
      :icon="X"
      :size="appControlIconSize[size]"
    />
  </button>
</template>
