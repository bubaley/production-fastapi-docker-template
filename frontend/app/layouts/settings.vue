<template>
  <AppLayout :drawer-sections="navigationSections">
    <template #header-context>
      <OrganizationPicker compact />
    </template>
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import type { NavigationSection } from '~/shared/components/layout/drawer/AppLayoutDrawer.vue'
import OrganizationPicker from '~/features/organization/components/OrganizationPicker.vue'
import { settingsNavigation } from '~/navigation/settings'

const { user } = useSession()

const navigationSections = computed<NavigationSection[]>(() => [
  {
    title: 'Настройки',
    items: settingsNavigation.filter((item) => !item.superuserOnly || user.value?.is_superuser),
  },
])
</script>
