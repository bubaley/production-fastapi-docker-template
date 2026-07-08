<template>
  <div
    v-if="isActive"
    v-bind="$attrs"
    class="app-tab-panel"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps<{
  tabValue: string
}>()

const activeRef = inject<Ref<string> | null>('app-tab-active', null)

const isActive = computed(() => {
  if (!activeRef) return false
  return activeRef.value === props.tabValue
})
</script>
