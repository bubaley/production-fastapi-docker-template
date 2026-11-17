<template>
  <div
    class="flex min-w-0 items-center transition-colors"
    :class="
      subtle ? 'gap-2 text-muted-foreground hover:text-foreground' : 'text-muted-foreground hover:text-foreground'
    "
  >
    <Flame
      :size="subtle ? 16 : compact ? 20 : 24"
      class="shrink-0"
      aria-hidden="true"
    />
    <div
      class="truncate"
      :class="subtle ? 'text-sm font-medium' : ['ml-1.5 font-semibold', compact ? 'text-sm' : 'text-sm sm:text-lg']"
    >
      {{ name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { Flame } from '@lucide/vue'

defineProps<{
  /** Fits a top bar: a smaller mark and one truncated line. */
  compact?: boolean
  /** A small muted mark for the sidebar footer: names the product without drawing the eye. */
  subtle?: boolean
}>()

const { name } = useAppConfig()
</script>
