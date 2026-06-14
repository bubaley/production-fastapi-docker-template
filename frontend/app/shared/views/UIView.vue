<template>
  <AppSection
    flat
    title="Welcome to the UIView!"
    description="FastAPI + Nuxt template for a quick start project"
  >
    <AppTitle size="lg">AppTitle: Root components</AppTitle>
    <div>
      <div class="text-sm fg-secondary mb-2">AppTemplateActions</div>
      <AppTemplateActions :actions="actions" />
    </div>
    <AppSection
      title-size="lg"
      title="AppSection with AppBlocks"
      description="Use AppBlock to display content in a styled container"
    >
      <AppBlock
        variant="outlined"
        icon="lucide:home"
        size="lg"
        color="primary"
        class="px-3"
      >
        Outlined AppBlock
      </AppBlock>
      <AppBlock
        variant="ghost"
        icon="lucide:home"
        size="lg"
        color="primary"
        class="px-3"
      >
        Ghost AppBlock
      </AppBlock>
      <AppBlock
        variant="ghost-outlined"
        icon="lucide:info"
        size="lg"
        color="orange"
        class="px-3"
      >
        Ghost Outlined AppBlock
      </AppBlock>
      <AppBlock
        variant="filled"
        icon="lucide:check-circle"
        size="lg"
        color="pink"
        class="px-3"
      >
        Filled AppBlock
      </AppBlock>
    </AppSection>
    <AppSection
      title-size="md"
      title="Page building essentials"
      description="Use these shared components when working through application pages."
      class="px-4 py-3"
    >
      <div class="space-y-3">
        <div class="space-y-2 text-sm">
          <div>
            <span class="font-medium mr-1">AppListTemplate</span>
            <span class="fg-secondary">- for consistent list page structure.</span>
          </div>
          <div>
            <span class="font-medium mr-1">AppDetailTemplate</span>
            <span class="fg-secondary">- for consistent detail page structure.</span>
          </div>
          <div>
            <span class="font-medium mr-1">AppBackButton</span>
            <span class="fg-secondary">- for predictable navigation back from detail flows.</span>
          </div>
          <div>
            <span class="font-medium mr-1">AppTemplateActions</span>
            <span class="fg-secondary">- for page-level action buttons.</span>
          </div>
          <div>
            <span class="font-medium mr-1">AppList</span>
            <span class="fg-secondary">- for rendering item collections with shared list behavior.</span>
          </div>
        </div>
      </div>
    </AppSection>
    <AppTitle
      size="lg"
      title="Other components"
    />
    <div>
      <div class="fg-secondary mb-2 text-sm">AppTabs</div>
      <AppTabs
        v-model="tab"
        query-key="home-tab"
        :tabs="tabs"
      >
        <div class="p-3 rounded-lg bg-surface-50 dark:bg-surface-900">
          <div class="mb-2 text-sm fg-secondary">Wrapper</div>
          <AppTabPanel tab-value="home">Home</AppTabPanel>
          <AppTabPanel tab-value="about">About</AppTabPanel>
          <AppTabPanel tab-value="contact">Contact</AppTabPanel>
        </div>
      </AppTabs>
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppSelect: {{ selectValue }}</div>
      <AppSelect
        v-model="selectValue"
        option-label="label"
        :options="tabs"
      />
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppMultiSelect: {{ multiSelectValue }}</div>
      <AppMultiSelect
        v-model="multiSelectValue"
        option-label="label"
        :options="tabs"
      />
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppInput: {{ inputValue }}</div>
      <AppInput
        v-model="inputValue"
        placeholder="Enter value"
      />
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppTextarea: {{ textareaValue }}</div>
      <AppTextarea
        v-model="textareaValue"
        auto-resize
        rows="3"
        placeholder="Enter long text"
      />
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppDatePicker: {{ dateValue }}</div>
      <AppDatePicker v-model="dateValue" />
      <div class="mt-2">
        AppDateLabel:
        <AppDateLabel
          type="date"
          :date="dateValue"
        />
      </div>
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppColorPicker: {{ colorValue }}</div>
      <AppColorPicker v-model="colorValue" />
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppImageLightbox</div>
      <AppButton
        label="Open gallery"
        severity="secondary"
        icon="lucide:image"
        @click="openLightbox()"
      />
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppButton + Modals</div>
      <div class="flex items-center gap-sm">
        <AppButton
          label="Open AppModal"
          severity="secondary"
          @click="modalVisible = true"
        />
        <AppButton
          label="Open AppConfirmModal"
          severity="secondary"
          @click="confirmModalVisible = true"
        />
      </div>
      <AppConfirmModal
        v-model="confirmModalVisible"
        title="AppConfirmModal"
        subtitle="Confirm the action"
        confirm-text="Confirm"
        decline-text="Decline"
        :confirm="() => notify({ severity: 'success', summary: 'Action confirmed' })"
        :decline="() => notify({ severity: 'error', summary: 'Action declined' })"
      >
        <div class="flex flex-col gap-3">
          <p class="">Modal content can contain any app components.</p>
        </div>
      </AppConfirmModal>
      <AppModal
        v-model="modalVisible"
        title="AppModal"
        subtitle="Opened from AppButton"
      >
        <div class="flex flex-col gap-3">
          <p class="">Modal content can contain any app components.</p>
          <AppButton
            label="Close"
            severity="secondary"
            class="ml-auto"
            @click="modalVisible = false"
          />
        </div>
      </AppModal>
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">useNotify</div>
      <div class="flex items-center gap-sm">
        <AppButton
          label="Show success notification"
          @click="showNotify('success')"
        />
        <AppButton
          label="Show info notification"
          severity="info"
          @click="showNotify('info')"
        />
        <AppButton
          label="Show warn notification"
          severity="warn"
          @click="showNotify('warn')"
        />
      </div>
    </div>
    <div>
      <div class="text-sm fg-secondary mb-2">AppPopover</div>
      <AppButton
        label="Open popover"
        icon="lucide:message-circle"
        severity="secondary"
      >
        <AppPopover
          title="AppPopover"
          subtitle="Click the button to toggle"
          class="p-3"
        >
          <div class="text-sm fg-secondary mt-3">Popover content is rendered inside the trigger component.</div>
        </AppPopover>
      </AppButton>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { AppTab } from '~/shared/ui/app/AppTabs.vue'
import { useAppImageLightboxStore } from '~/shared/ui/app/stores/useAppImageLightboxStore'

const tab = ref('home')
const tabs = ref<AppTab[]>([
  { label: 'Home', value: 'home' },
  { label: 'About', value: 'about' },
  { label: 'Contact', value: 'contact' },
  { label: 'Empty', value: 'empty' },
])
const selectValue = ref(tabs.value[0])
const multiSelectValue = ref<AppTab[]>(tabs.value.filter((_, index) => [0, 2].includes(index)))
const inputValue = ref('')
const textareaValue = ref('')
const dateValue = ref<string | null>(dayjs().format('YYYY-MM-DD'))
const colorValue = ref('#3b82f6')
const modalVisible = ref(false)
const confirmModalVisible = ref(false)
const { notify } = useNotify()
const imageLightbox = useAppImageLightboxStore()
const lightboxSources = [
  'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=900&q=80',
]

const openLightbox = (index = 0) => {
  imageLightbox.open(lightboxSources, index)
}

const showNotify = (severity: 'success' | 'info' | 'warn' | 'error' | 'secondary' | 'contrast' = 'success') => {
  notify({
    severity,
    summary: `useNotify: ${severity}`,
    detail: 'Notification was shown from the home page demo.',
  })
}

const actions = ref<AppTemplateAction[]>([
  {
    label: 'Settings',
    icon: 'lucide:settings',
    onClick: () => navigateTo({ name: 'settings-organizations' }),
  },
  {
    label: 'Switch organization',
    icon: 'lucide:building-2',
    severity: 'secondary',
    onClick: () => navigateTo({ name: 'home-setup' }),
  },
])
</script>
