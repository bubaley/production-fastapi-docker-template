<template>
  <AppSection
    flat
    title="UI kit"
    description="Live gallery of shared app components. Open a tab to inspect variants."
    class="pb-8"
    :back-action="() => navigateTo({ name: 'home' })"
  >
    <AppTabs
      v-model="tab"
      query-key="ui-tab"
      :tabs="tabs"
    >
      <AppTabPanel tab-value="layout">
        <UiLayoutShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="blocks">
        <UiBlocksShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="buttons">
        <UiButtonsShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="icons">
        <UiIconsShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="labels">
        <UiLabelsShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="smart-date">
        <UiSmartDateShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="forms">
        <UiFormsShowcase />
      </AppTabPanel>
      <AppTabPanel tab-value="overlays">
        <UiOverlaysShowcase />
      </AppTabPanel>
    </AppTabs>
  </AppSection>
</template>

<script setup lang="ts">
import type { AppTab } from '~/shared/ui/app/AppTabs.vue'
import UiBlocksShowcase from '../components/UiBlocksShowcase.vue'
import UiButtonsShowcase from '../components/UiButtonsShowcase.vue'
import UiFormsShowcase from '../components/UiFormsShowcase.vue'
import UiIconsShowcase from '../components/UiIconsShowcase.vue'
import UiLabelsShowcase from '../components/UiLabelsShowcase.vue'
import UiLayoutShowcase from '../components/UiLayoutShowcase.vue'
import UiOverlaysShowcase from '../components/UiOverlaysShowcase.vue'
import UiSmartDateShowcase from '../components/UiSmartDateShowcase.vue'

const tab = ref('layout')
const tabs = ref<AppTab[]>([
  { label: 'Layout', value: 'layout' },
  { label: 'Blocks', value: 'blocks' },
  { label: 'Buttons', value: 'buttons' },
  { label: 'Icons', value: 'icons' },
  { label: 'Labels', value: 'labels' },
  { label: 'Smart Date', value: 'smart-date' },
  { label: 'Forms', value: 'forms' },
  { label: 'Overlays', value: 'overlays' },
])
</script>
