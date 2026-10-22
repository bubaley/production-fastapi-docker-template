<script setup lang="ts">
withDefaults(defineProps<{ bordered?: boolean }>(), { bordered: true })
</script>

<template>
  <section
    :class="bordered ? 'rounded-md border border-border' : 'border-0'"
    class="flex h-full min-h-0 min-w-0 w-full flex-col items-stretch overflow-hidden bg-background"
  >
    <slot />
  </section>
</template>
