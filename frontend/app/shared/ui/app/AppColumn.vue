<script setup lang="ts">
export interface AppColumnProps {
  field?: string
  header?: string
  format?: (data: any, row: { data: any; index: number }) => unknown
  headerClass?: string
  bodyClass?: string
  style?: string | Record<string, string>
}
defineProps<AppColumnProps>()
</script>
<template><slot /></template>
