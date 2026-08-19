<template>
  <div class="flex min-w-0 flex-col gap-4">
    <div
      v-if="label || caption"
      class="flex items-center gap-4"
    >
      <span
        v-if="label"
        class="text-sm font-medium"
      >
        {{ label }}
      </span>
      <span
        v-if="caption"
        class="text-sm fg-tertiary"
      >
        {{ caption }}
      </span>
    </div>
    <div
      class="flex flex-wrap items-center gap-4"
      :class="[contentClass, { 'flex-col items-stretch': stacked }]"
    >
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  caption?: string
  stacked?: boolean
  contentClass?: string
}>()
</script>
