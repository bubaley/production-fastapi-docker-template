<template>
  <AppLayout :drawer-sections="navigationSections">
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import type { NavigationSection } from '~/shared/components/layout/drawer/AppLayoutDrawer.vue'

const navigationSections = ref<NavigationSection[]>([
  {
    title: 'Menu',
    items: [{ to: { name: 'home' }, label: 'Home', icon: 'lucide:home' }],
  },
])
</script>
