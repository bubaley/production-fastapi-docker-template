<script setup lang="ts">
import UiControlsShowcase from '../components/UiControlsShowcase.vue'
import UiFormsShowcase from '../components/UiFormsShowcase.vue'
import UiOverlaysShowcase from '../components/UiOverlaysShowcase.vue'
import UiLayoutShowcase from '../components/UiLayoutShowcase.vue'
import UiTemplatesShowcase from '../components/UiTemplatesShowcase.vue'
const tab = ref('components')
const colorMode = useColorMode()
const tabs = [{ label: 'Components', value: 'components' }, { label: 'Layout', value: 'layout' }, { label: 'Templates', value: 'templates' }]
</script>
<template>
  <AppPageView
    title="UI library"
    description="Components, states and reusable templates for new projects."
  >
    <template #actions>
      <ClientOnly>
        <AppButton
          variant="outline"
          size="sm"
          :icon="colorMode.value === 'dark' ? 'lucide:sun' : 'lucide:moon'"
          :label="colorMode.value === 'dark' ? 'Light mode' : 'Dark mode'"
          @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
        />
        <template #fallback>
          <AppButton
            variant="outline"
            size="sm"
            icon="lucide:sun-moon"
            label="Appearance"
            disabled
          />
        </template>
      </ClientOnly>
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
        <AppTabPanel tab-value="layout"><UiLayoutShowcase class="py-6" /></AppTabPanel>
        <AppTabPanel tab-value="templates"><UiTemplatesShowcase class="py-6" /></AppTabPanel>
      </AppTabs>
    </div>
  </AppPageView>
</template>
