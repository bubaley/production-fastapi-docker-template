<template>
  <main
    class="min-h-0 min-w-0 flex-1 overflow-auto"
    :class="[bordered && 'rounded-lg border border-border', !noPadding && 'p-4']"
  >
    <slot />
  </main>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ bordered?: boolean; noPadding?: boolean }>(), { noPadding: true })
</script>
