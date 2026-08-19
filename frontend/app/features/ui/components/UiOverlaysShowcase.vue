<template>
  <UiShowcaseSection
    title="Overlays & feedback"
    description="Modals, menus, lightbox and toast notifications."
  >
    <UiShowcaseItem label="AppModal">
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
    </UiShowcaseItem>

    <UiShowcaseItem label="AppMenu">
      <AppButton
        label="Parent trigger"
        icon="lucide:ellipsis"
        severity="secondary"
      >
        <AppMenu :actions="menuActions" />
      </AppButton>
      <AppMenu
        label="Custom content"
        subtitle="Trigger slot + default slot"
      >
        <template #trigger>
          <AppButton
            label="Trigger slot"
            icon="lucide:panel-bottom"
            severity="secondary"
          />
        </template>
        <div class="px-2 py-1.5 text-sm fg-secondary">Any content can go here.</div>
      </AppMenu>
      <AppMenu
        v-model="menuOpen"
        label="Actions"
        :actions="menuActions"
      >
        <template #trigger>
          <AppButton
            :label="menuOpen ? 'Opened' : 'v-model'"
            icon="lucide:toggle-left"
            severity="secondary"
          />
        </template>
      </AppMenu>
      <AppButton
        label="Open via v-model"
        severity="secondary"
        @click="menuOpen = true"
      />
      <div class="cursor-context-menu rounded-md border border-dashed border-surface-300 px-3 py-2 text-sm fg-secondary dark:border-surface-700">
        Right click (cursor mode)
        <AppMenu
          context
          mode="cursor"
          :actions="menuActions"
        />
      </div>
    </UiShowcaseItem>

    <UiShowcaseItem label="AppImageLightbox">
      <AppButton
        label="Open gallery"
        severity="secondary"
        icon="lucide:image"
        @click="imageLightbox.open(lightboxSources)"
      />
    </UiShowcaseItem>

    <UiShowcaseItem label="useNotify">
      <AppButton
        v-for="item in notifyButtons"
        :key="item.severity"
        :label="item.label"
        :severity="item.buttonSeverity"
        @click="showNotify(item.severity)"
      />
    </UiShowcaseItem>

    <AppConfirmModal
      v-model="confirmModalVisible"
      title="AppConfirmModal"
      subtitle="Confirm the action"
      confirm-text="Confirm"
      decline-text="Decline"
      :confirm="() => notify({ severity: 'success', summary: 'Action confirmed' })"
      :decline="() => notify({ severity: 'error', summary: 'Action declined' })"
    >
      <p>Modal content can contain any app components.</p>
    </AppConfirmModal>

    <AppModal
      v-model="modalVisible"
      title="AppModal"
      subtitle="Opened from AppButton"
    >
      <div class="flex flex-col gap-3">
        <p>Modal content can contain any app components.</p>
        <AppButton
          label="Close"
          severity="secondary"
          class="ml-auto"
          @click="modalVisible = false"
        />
      </div>
    </AppModal>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import type { AppButtonProps } from '~/shared/ui/app/AppButton.vue'
import type { AppListAction } from '~/shared/ui/app/AppListActions.vue'
import { useAppImageLightboxStore } from '~/shared/ui/app/stores/useAppImageLightboxStore'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const modalVisible = ref(false)
const confirmModalVisible = ref(false)
const menuOpen = ref(false)
const { notify } = useNotify()
const imageLightbox = useAppImageLightboxStore()
const lightboxSources = [
  'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=900&q=80',
]

const notifyButtons: { label: string; severity: 'success' | 'info' | 'warn' | 'error'; buttonSeverity?: AppButtonProps['severity'] }[] = [
  { label: 'Success', severity: 'success' },
  { label: 'Info', severity: 'info', buttonSeverity: 'info' },
  { label: 'Warn', severity: 'warn', buttonSeverity: 'warn' },
  { label: 'Error', severity: 'error', buttonSeverity: 'danger' },
]

const showNotify = (severity: 'success' | 'info' | 'warn' | 'error') => {
  notify({
    severity,
    summary: `useNotify: ${severity}`,
    detail: 'Notification was shown from the UI kit.',
  })
}

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const menuActions = computed<AppListAction[]>(() => [
  { label: 'Rename', icon: 'lucide:pencil', action: () => notify({ summary: 'Rename' }) },
  {
    label: 'Load async',
    icon: 'lucide:loader-circle',
    action: async () => {
      await wait(800)
      notify({ summary: 'Async action finished' })
    },
  },
  {
    label: 'Delete',
    icon: 'lucide:trash-2',
    severity: 'danger',
    action: () => notify({ severity: 'error', summary: 'Delete' }),
  },
])
</script>
