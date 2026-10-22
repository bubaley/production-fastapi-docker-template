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
    title: 'Меню',
    items: [{ to: { name: 'home' }, label: 'Главная', icon: 'lucide:home' }],
  },
])
</script>
