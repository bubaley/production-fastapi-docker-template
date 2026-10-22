<template>
  <AppLayout :drawer-sections="navigationSections">
    <template #header-context>
      <OrganizationPicker compact />
    </template>
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import { Building, User, Users } from '@lucide/vue'
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import type { NavigationSection } from '~/shared/components/layout/drawer/AppLayoutDrawer.vue'
import OrganizationPicker from '~/features/organization/components/OrganizationPicker.vue'

const { user } = useSession()

const navigationSections = computed<NavigationSection[]>(() => {
  const result: NavigationSection[] = [
    {
      title: 'Настройки',
      items: [
        { to: { name: 'settings-profile' }, label: 'Профиль', icon: User },
        { to: { name: 'settings-organizations' }, label: 'Организации', icon: Building },
      ],
    },
  ]
  if (user.value?.is_superuser) {
    result[0]?.items.push({ to: { name: 'settings-users' }, label: 'Пользователи', icon: Users })
  }
  return result
})
</script>
