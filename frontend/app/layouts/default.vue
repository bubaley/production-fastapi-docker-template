<template>
  <AppLayout :drawer-sections="navigationSections">
    <template #header-context>
      <OrganizationPicker compact />
    </template>
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import { House } from '@lucide/vue'
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import type { NavigationSection } from '~/shared/components/layout/drawer/AppLayoutDrawer.vue'
import OrganizationPicker from '~/features/organization/components/OrganizationPicker.vue'

const navigationSections: NavigationSection[] = [
  {
    title: 'Меню',
    items: [{ to: { name: 'home' }, label: 'Главная', icon: House }],
  },
]
</script>
