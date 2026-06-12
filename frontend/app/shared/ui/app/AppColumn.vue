<template>
  <Column v-bind="$attrs">
    <slot />
  </Column>
</template>

<script setup lang="ts">
import Column from 'primevue/column'
import type { ColumnProps } from 'primevue/column'
export interface AppColumnProps extends ColumnProps {
  test?: string
  format?: (data: any, row: any) => string | null | number
}

defineProps<AppColumnProps>()
</script>
