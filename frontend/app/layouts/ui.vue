<template>
  <AppLayout>
    <template #sidebar-header>
      <AppSidebarLink :item="{ to: { name: 'home' }, label: 'Back to app', icon: ArrowLeft }" />
    </template>
    <template #topbar>
      <span class="px-1 text-sm font-medium">UI catalogue</span>
    </template>
    <template #sidebar>
      <AppSidebarNav
        :sections="uiNavigation"
        label="UI catalogue"
      />
    </template>
    <!-- The catalogue is public: theme and palette controls replace the account menu. -->
    <template #sidebar-footer>
      <AppThemeSwitcher
        locale="en"
        class="px-1"
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
import { uiNavigation } from '~/navigation/ui'
</script>
