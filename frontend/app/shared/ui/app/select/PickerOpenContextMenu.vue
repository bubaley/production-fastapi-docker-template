<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUpRight } from '@lucide/vue'
import AppMenu, { type AppMenuAction } from '../AppMenu.vue'

const props = defineProps<{
  enabled?: boolean
  label: string
}>()
const emit = defineEmits<{ open: [] }>()
const actions = computed<AppMenuAction[]>(() => [
  {
    value: 'open',
    label: props.label,
    icon: ArrowUpRight
  }
])
const selectAction = (action: AppMenuAction) => {
  if (action.value === 'open') emit('open')
}
</script>

<template>
  <AppMenu
    v-if="enabled"
    context
    :actions="actions"
    @select="selectAction"
  >
    <template #trigger><slot /></template>
  </AppMenu>
  <slot v-else />
</template>
