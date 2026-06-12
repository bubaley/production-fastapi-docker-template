<template>
  <AppButton
    icon="lucide:chevron-left"
    severity="secondary"
    variant="text"
    :icon-size="iconSize"
    @click="backAction"
  />
</template>

<script setup lang="ts">
export type AppBackButtonProps = {
  backAction?: () => void
  iconSize?: number
}

const props = withDefaults(defineProps<AppBackButtonProps>(), {
  iconSize: 22,
})
</script>
