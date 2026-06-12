<template>
  <div class="flex items-center gap-2">
    <Icon
      v-if="icon"
      size="16px"
      :name="icon"
      class="fg-secondary"
    />
    <div class="fg-secondary">{{ label }}</div>
    <slot v-if="$slots.default" />
    <div v-else>{{ value }}</div>
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  icon?: string
  label?: string
  value?: string | null | number
}>()
</script>
