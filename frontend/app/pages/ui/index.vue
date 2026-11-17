<template></template>

<script setup lang="ts">
import { uiSections } from '~/features/ui/catalog'

definePageMeta({
  redirect: () => ({ name: 'ui-section', params: { section: uiSections[0]?.key ?? 'colors' } }),
})
</script>
