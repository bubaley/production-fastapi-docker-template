<script setup lang="ts">
import UiControlsShowcase from '../components/UiControlsShowcase.vue'
import UiFormsShowcase from '../components/UiFormsShowcase.vue'
import UiOverlaysShowcase from '../components/UiOverlaysShowcase.vue'
import UiLayoutShowcase from '../components/UiLayoutShowcase.vue'
import UiTemplatesShowcase from '../components/UiTemplatesShowcase.vue'
import UiTokensShowcase from '../components/UiTokensShowcase.vue'
const tab = ref('components')
const tabs = [
  { label: 'Components', value: 'components' },
  { label: 'Tokens', value: 'tokens' },
  { label: 'Layout', value: 'layout' },
  { label: 'Templates', value: 'templates' },
]
</script>
<template>
  <AppPageView
    title="UI library"
    description="Living catalogue of tokens, App* components, states and templates. English by design; product screens are Russian."
  >
    <template #subheader>
      <div class="max-w-md pb-3">
        <AppThemeSwitcher locale="en" />
      </div>
    </template>
    <div class="mx-auto w-full max-w-6xl pb-8">
      <AppTabs
        v-model="tab"
        aria-label="Sections"
        :tabs="tabs"
        query-key="tab"
      >
        <AppTabPanel tab-value="components">
          <div class="space-y-10 py-6">
            <UiControlsShowcase />
            <UiFormsShowcase />
            <UiOverlaysShowcase />
          </div>
        </AppTabPanel>
        <AppTabPanel tab-value="tokens"><UiTokensShowcase class="py-6" /></AppTabPanel>
        <AppTabPanel tab-value="layout"><UiLayoutShowcase class="py-6" /></AppTabPanel>
        <AppTabPanel tab-value="templates"><UiTemplatesShowcase class="py-6" /></AppTabPanel>
      </AppTabs>
    </div>
  </AppPageView>
</template>
