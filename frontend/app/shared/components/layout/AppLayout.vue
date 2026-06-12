<template>
  <div class="flex min-h-0 h-screen flex-col">
    <AppLayoutHeader />

    <div class="flex min-h-0 flex-1">
      <AppLayoutDrawer
        :sections="drawerSections"
        class="pl-1 pb-1"
      >
        <template #after>
          <slot name="drawer-after" />
        </template>
      </AppLayoutDrawer>
      <AppPageLayout bordered>
        <slot />
      </AppPageLayout>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppLayoutHeader from '~/shared/components/layout/header/AppLayoutHeader.vue'
import AppLayoutDrawer, { type NavigationSection } from '~/shared/components/layout/drawer/AppLayoutDrawer.vue'
import AppPageLayout from './AppPageLayout.vue'

defineProps<{
  drawerSections?: NavigationSection[]
}>()
</script>
