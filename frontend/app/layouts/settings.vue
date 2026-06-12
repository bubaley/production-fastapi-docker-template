<template>
  <AppLayout :drawer-sections="navigationSections">
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import type { NavigationSection } from '~/shared/components/layout/drawer/AppLayoutDrawer.vue'

const { session } = useAuth()

const navigationSections = computed<NavigationSection[]>(() => {
  const result = [
    {
      title: 'Settings',
      items: [
        { to: { name: 'settings-profile' }, label: 'Profile', icon: 'lucide:user' },
        { to: { name: 'settings-organizations' }, label: 'Organizations', icon: 'lucide:building' },
      ],
    },
  ]
  if (session.value?.is_superuser) {
    result[0]?.items.push({ to: { name: 'settings-users' }, label: 'Users', icon: 'lucide:users' })
  }
  return result
})
</script>
