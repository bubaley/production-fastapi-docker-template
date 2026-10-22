<script setup lang="ts">
import { Ellipsis, Image, PanelsTopLeft, Pencil, Trash2 } from '@lucide/vue'
import type { AppMenuAction } from '~/shared/ui/app/AppMenu.vue'
import { useAppImageLightboxStore } from '~/shared/ui/app/stores/useAppImageLightboxStore'
const toast = useToast()
const lightbox = useAppImageLightboxStore()
// Inline SVGs keep the demo offline.
const sampleImage = (label: string, color: string) =>
  `data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600"><rect width="100%" height="100%" fill="${color}"/><text x="50%" y="50%" fill="#fff" font-family="sans-serif" font-size="48" text-anchor="middle" dominant-baseline="middle">${label}</text></svg>`,
  )}`
const images = [sampleImage('Image 1', '#2563eb'), sampleImage('Image 2', '#16a34a'), sampleImage('Image 3', '#c2410c')]
const modal = ref(false)
const confirm = ref(false)
const drawer = ref(false)
const unsaved = ref(false)
const modalName = ref('Working project')
const color = ref<string | null>('#7779ed')
const icon = ref<string | null>('folder')
const actions: AppMenuAction[] = [
  {
    label: 'Open modal',
    icon: PanelsTopLeft,
    action: () => {
      modal.value = true
    },
  },
  { label: 'Rename', icon: Pencil, action: () => toast.default('Rename requested') },
  {
    label: 'Delete',
    icon: Trash2,
    destructive: true,
    separatorBefore: true,
    action: () => {
      confirm.value = true
    },
  },
]
</script>
<template>
  <div class="space-y-10">
    <AppSection
      title="Overlays, menus and toasts"
      description="Try nested pickers, Escape dismissal and focus restoration."
    >
      <AppCard>
        <AppTemplateActions
          :actions="[
            {
              label: 'Open Modal',
              icon: PanelsTopLeft,
              action: () => {
                modal = true
              },
            },
            {
              label: 'Confirmation',
              variant: 'outline',
              action: () => {
                confirm = true
              },
            },
            {
              label: 'Drawer',
              variant: 'outline',
              action: () => {
                drawer = true
              },
            },
            {
              label: 'Unsaved changes',
              variant: 'outline',
              action: () => {
                unsaved = true
              },
            },
          ]"
        />
        <div class="mt-4 flex flex-wrap items-center gap-3">
          <AppMenu
            :actions="actions"
            label="Project actions"
          >
            <template #trigger>
              <AppButton
                variant="outline"
                label="Open menu"
                :icon="Ellipsis"
              />
            </template>
          </AppMenu>
          <AppButton
            variant="ghost"
            label="Default toast"
            @click="toast.default('Changes saved', { description: 'You can continue working.' })"
          />
          <AppButton
            variant="ghost"
            label="Error toast"
            @click="toast.error('Could not save', { description: 'Please try again.' })"
          />
          <AppButton
            variant="outline"
            label="Image lightbox"
            :icon="Image"
            @click="lightbox.open(images, 0)"
          />
        </div>
      </AppCard>
    </AppSection>
    <AppSection
      title="Color and appearance"
      description="Color palette and searchable Lucide icon catalog."
    >
      <AppCard class="space-y-5">
        <AppColorPicker
          v-model="color"
          label="Project color"
        />
        <div class="flex flex-wrap items-center gap-4">
          <AppAppearancePicker
            v-model:icon="icon"
            v-model:color="color"
            subject="product"
          />
          <span class="text-sm text-muted-foreground">Project icon and color</span>
        </div>
      </AppCard>
    </AppSection>
    <AppModal
      v-model="modal"
      close-label="Close"
      title="Project settings"
      description="Example form inside a modal."
    >
      <div class="space-y-4">
        <AppInput
          v-model="modalName"
          label="Name"
        /><AppDatePicker
          label="Due date"
          clearable
        /><AppColorPicker v-model="color" />
      </div>
      <template #footer
        ><AppTemplateActions
          :actions="[
            {
              label: 'Cancel',
              variant: 'secondary',
              action: () => {
                modal = false
              },
            },
            {
              label: 'Save',
              action: () => {
                toast.default('Changes saved')
                modal = false
              },
            },
          ]"
      /></template>
    </AppModal>
    <AppConfirmModal
      v-model="confirm"
      decline-text="Cancel"
      close-label="Close"
      title="Delete project?"
      subtitle="This is a demo. Your data will not change."
      confirm-text="Delete"
      :confirm-props="{ variant: 'destructive' }"
      :confirm="
        () => {
          toast.default('Action confirmed')
        }
      "
    />
    <AppUnsavedChangesModal
      v-model="unsaved"
      title="Save changes?"
      description="You have unsaved changes."
      save-label="Save"
      discard-label="Discard"
      cancel-label="Cancel"
      close-label="Close"
      @save="
        () => {
          toast.default('Changes saved')
          unsaved = false
        }
      "
      @discard="unsaved = false"
    />
    <AppDrawer
      v-model="drawer"
      close-label="Close"
      description="Additional settings and actions."
      overlay
      side="right"
      :width="360"
      title="Page settings"
    >
      <AppSection
        title="Page settings"
        description="Additional settings without leaving the page."
      >
        <AppInput
          label="View name"
          model-value="My projects"
        />
        <AppDatePicker
          label="Due date"
          clearable
        />
        <AppButton
          variant="outline"
          label="Open nested Modal"
          @click="modal = true"
        />
      </AppSection>
    </AppDrawer>
  </div>
</template>
