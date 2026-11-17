<script setup lang="ts">
import { Activity, LayoutGrid, Settings } from '@lucide/vue'
import UiDemo from '../../components/UiDemo.vue'

const tab = ref('overview')
const tabs = [
  { label: 'Overview', value: 'overview', icon: LayoutGrid },
  { label: 'Activity', value: 'activity', icon: Activity },
  { label: 'Settings', value: 'settings', icon: Settings },
  { label: 'Disabled', value: 'disabled', disabled: true },
]
</script>

<template>
  <UiDemo
    title="Segment tabs"
    code='v-model :tabs query-key="tab"'
    description="Sections of one screen. With query-key the active tab survives reload and can be linked; on phones the tabs scroll."
  >
    <AppTabs
      v-model="tab"
      aria-label="Project sections"
      :tabs="tabs"
      query-key="tab"
    >
      <AppTabPanel tab-value="overview">
        <p class="pt-4 text-sm">Overview content.</p>
      </AppTabPanel>
      <AppTabPanel tab-value="activity">
        <p class="pt-4 text-sm">Activity content.</p>
      </AppTabPanel>
      <AppTabPanel tab-value="settings">
        <p class="pt-4 text-sm">Settings content.</p>
      </AppTabPanel>
    </AppTabs>
  </UiDemo>
</template>
