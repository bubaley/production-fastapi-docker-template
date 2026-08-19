<template>
  <div class="flex flex-col gap-6">
    <AppTitle
      v-if="title"
      size="lg"
      :title="title"
      :subtitle="description"
    />
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  description?: string
}>()
</script>
