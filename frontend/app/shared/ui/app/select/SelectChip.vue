<script setup lang="ts">
import { X } from '@lucide/vue'
defineProps<{ label: string; disabled?: boolean; removeLabel: string }>()
defineEmits<{ remove: [] }>()
</script>
<template>
  <span
    class="relative z-10 inline-flex max-w-full items-center gap-1 rounded-sm border border-border bg-secondary pl-2 pr-1 py-0.5 text-xs"
  ><span class="min-w-0 truncate"><slot>{{ label }}</slot></span><button
    type="button"
    class="pointer-events-auto grid size-5 shrink-0 place-items-center rounded-sm text-muted-foreground hover:bg-accent hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none"
    :disabled="disabled"
    :aria-label="`${removeLabel}: ${label}`"
    @click.stop="$emit('remove')"
  >
    <X class="size-3" /></button></span>
</template>
