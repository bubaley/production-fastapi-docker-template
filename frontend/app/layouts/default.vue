<template>
  <AppLayout>
    <template #sidebar-header>
      <OrganizationSwitcher />
    </template>
    <template #sidebar>
      <AppSidebarNav :sections="sections" />
    </template>
    <slot />
    <!-- A user without any organization sees the shell with this modal over it until they create one. -->
    <OrganizationCreateModal
      :model-value="needsOrganization"
      required
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { House } from '@lucide/vue'
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import AppSidebarNav from '~/shared/components/layout/sidebar/AppSidebarNav.vue'
import type { SidebarSection } from '~/shared/components/layout/sidebar/types'
import OrganizationCreateModal from '~/features/organization/components/OrganizationCreateModal.vue'
import OrganizationSwitcher from '~/features/organization/components/OrganizationSwitcher.vue'

const sections: SidebarSection[] = [{ items: [{ to: { name: 'home' }, label: 'Главная', icon: House }] }]

const setupStore = useSetupStore()
const route = useRoute()
// `restored` is client-only, so SSR never renders the modal before the selection is known.
const needsOrganization = computed<boolean>(
  () => setupStore.state.restored && !setupStore.state.organization && route.meta.organization !== false,
)
</script>
