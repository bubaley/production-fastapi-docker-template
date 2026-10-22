<template>
  <AppSelect
    v-model="setupStore.state.organization"
    :class="selectClass"
    :filter="false"
    option-label="name"
    :repo="useRepo('organization')"
    :variant="compact ? 'ghost' : 'outline'"
    aria-label="Организация"
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

</script>
