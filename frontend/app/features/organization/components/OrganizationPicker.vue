<template>
  <AppSelect
    v-model="setupStore.state.organization"
    :class="selectClass"
    :filter="false"
    option-label="name"
    :resource="organizationResource"
    :variant="compact ? 'ghost' : 'outline'"
    aria-label="Организация"
    class="bg-transparent!"
  />
</template>

<script setup lang="ts">
import { organizationResource } from '../resources/organization'

const props = withDefaults(defineProps<{ compact?: boolean }>(), {
  compact: false,
})

const setupStore = useSetupStore()

const selectClass = computed(() => {
  return props.compact ? '!border-none !shadow-none' : 'max-w-sm w-full'
})
</script>
