<template>
  <AppSelect
    v-model="setupStore.state.organization"
    :class="selectClass"
    :filter="false"
    option-label="name"
    :repo="useRepo('organization')"
    :pt="selectPt"
    class="bg-transparent!"
  />
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{ compact?: boolean }>(), {
  compact: false,
})

const setupStore = useSetupStore()

const selectClass = computed(() => {
  return props.compact ? '!border-none !shadow-none' : 'max-w-sm w-full'
})

const selectPt = computed(() => {
  if (!props.compact) return undefined
  return {
    label: '!pr-0 text-surface-600! dark:text-surface-400! text!',
  }
})
</script>
