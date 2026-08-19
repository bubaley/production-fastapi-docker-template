<template>
  <UiShowcaseSection
    title="Page chrome"
    description="Templates and navigation pieces used on list and detail pages."
  >
    <UiShowcaseItem
      stacked
      :label="`AppTabs: ${tab}`"
    >
      <AppTabs
        v-model="tab"
        :tabs="tabs"
      >
        <div class="rounded-lg bg-surface-50 p-3 dark:bg-surface-900">
          <AppTabPanel
            v-for="item in tabs"
            :key="item.value"
            :tab-value="item.value"
          >
            {{ item.label }} panel
          </AppTabPanel>
        </div>
      </AppTabs>
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      label="AppTemplateActions"
      caption="Две и больше кнопок в ряд — только этот компонент, не несколько AppButton подряд"
    >
      <AppTemplateActions
        size="small"
        :actions="templateActions"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      label="useActionState"
      caption="Одна кнопка или модалка: loading + execute, без своего try/finally"
    >
      <AppButton
        label="Сохранить"
        icon="lucide:save"
        :loading="saveState.loading.value"
        @click="saveState.execute"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      label="Page building"
    >
      <div class="space-y-2 text-sm">
        <div
          v-for="item in buildingBlocks"
          :key="item.name"
        >
          <span class="mr-1 font-medium">{{ item.name }}</span>
          <span class="fg-secondary">— {{ item.hint }}</span>
        </div>
      </div>
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import type { AppTab } from '~/shared/ui/app/AppTabs.vue'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const tabs: AppTab[] = [
  { label: 'Home', value: 'home' },
  { label: 'About', value: 'about' },
  { label: 'Contact', value: 'contact' },
]
const tab = ref(tabs[0]!.value)

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const saveState = useActionState(
  async () => {
    await wait(800)
  },
  { successNotification: 'Сохранено' },
)

const templateActions: AppTemplateAction[] = [
  {
    label: 'Сохранить',
    icon: 'lucide:save',
    action: async () => {
      await wait(800)
    },
    successNotification: 'Сохранено',
  },
  { label: 'Отмена', icon: 'lucide:x', severity: 'secondary' },
  { label: 'Ещё', icon: 'lucide:ellipsis', severity: 'secondary' },
]

const buildingBlocks = [
  { name: 'AppListTemplate', hint: 'consistent list page structure' },
  { name: 'AppDetailTemplate', hint: 'consistent detail page structure' },
  { name: 'AppBackButton', hint: 'navigation back from detail flows' },
  { name: 'AppTemplateActions', hint: 'row of 2+ buttons — never side-by-side AppButtons' },
  { name: 'AppList', hint: 'item collections with shared list behavior' },
]
</script>
