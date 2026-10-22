<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ label?: string; locale?: 'ru' | 'en' }>(), { locale: 'ru' })
const accessibleLabel = computed(() => props.label || (props.locale === 'en' ? 'No data' : 'Нет данных'))
</script>

<template>
  <span
    class="inline-block text-muted-foreground"
    :aria-label="accessibleLabel"
    :title="accessibleLabel"
  >—</span>
</template>
