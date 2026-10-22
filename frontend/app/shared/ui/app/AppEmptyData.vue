<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ label?: string }>()
const accessibleLabel = computed(() => props.label || 'Нет данных')
</script>

<template>
  <span
    class="inline-block text-muted-foreground"
    :aria-label="accessibleLabel"
    :title="accessibleLabel"
    >—</span
  >
</template>
