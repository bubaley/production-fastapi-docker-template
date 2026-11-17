<template>
  <AppLayout>
    <template #sidebar-header>
      <AppSidebarLink :item="{ to: { name: 'home' }, label: 'Назад', icon: ArrowLeft }" />
    </template>
    <template #topbar>
      <span class="px-1 text-sm font-medium">Настройки</span>
    </template>
    <template #sidebar>
      <div
        v-if="hasOrganization"
        class="pb-3"
      >
        <OrganizationSwitcher />
      </div>
      <AppSidebarNav
        :sections="sections"
        label="Настройки"
      />
    </template>
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import { ArrowLeft } from '@lucide/vue'
import AppLayout from '~/shared/components/layout/AppLayout.vue'
import AppSidebarLink from '~/shared/components/layout/sidebar/AppSidebarLink.vue'
import AppSidebarNav from '~/shared/components/layout/sidebar/AppSidebarNav.vue'
import type { SidebarSection } from '~/shared/components/layout/sidebar/types'
import OrganizationSwitcher from '~/features/organization/components/OrganizationSwitcher.vue'
import { settingsNavigation, settingsSections } from '~/navigation/settings'

const setupStore = useSetupStore()
const { user } = useSession()
const hasOrganization = computed<boolean>(() => Boolean(setupStore.state.organization))
const isSuperuser = computed<boolean>(() => Boolean(user.value?.is_superuser))

const sections = computed<SidebarSection[]>(() =>
  settingsSections
    .map(({ key, title }) => ({
      title,
      items: settingsNavigation
        .filter((item) => (item.section ?? 'organization') === key)
        // The profile works before an organization is chosen; organization-scoped pages do not.
        .filter(() => key !== 'organization' || hasOrganization.value)
        .filter((item) => !item.superuserOnly || isSuperuser.value),
    }))
    .filter((section) => section.items.length > 0),
)
</script>
