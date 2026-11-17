<template>
  <UiSectionView :section-key="sectionKey" />
</template>

<script setup lang="ts">
import { findUiSection } from '~/features/ui/catalog'
import UiSectionView from '~/features/ui/views/UiSectionView.vue'

// An unknown section is a 404, not an empty page.
definePageMeta({ validate: (route) => Boolean(findUiSection(String(route.params.section))) })

const route = useRoute()
const sectionKey = computed<string>(() => String(route.params.section))
</script>
