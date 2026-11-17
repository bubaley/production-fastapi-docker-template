<script setup lang="ts">
import { PanelsTopLeft } from '@lucide/vue'
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
const modal = ref(false)
const confirm = ref(false)
const unsaved = ref(false)
const modalName = ref('Working project')
const dueAt = ref<string | null>('2026-09-27T14:30')
const color = ref<string | null>('#7779ed')
</script>

<template>
  <UiDemo
    title="Modal, confirmation, unsaved changes"
    code="AppModal v-model title description #footer · AppConfirmModal :confirm · AppUnsavedChangesModal"
    description="Try nested pickers inside the modal, Escape dismissal and focus return to the trigger."
  >
    <AppTemplateActions
      :actions="[
        {
          label: 'Open modal',
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
          label: 'Unsaved changes',
          variant: 'outline',
          action: () => {
            unsaved = true
          },
        },
      ]"
    />
  </UiDemo>
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
        v-model="dueAt"
        label="Due date and time"
        time
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
            label: 'Save as draft',
            variant: 'outline',
            action: () => {
              toast.default('Draft saved')
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
    :confirm="() => void toast.default('Action confirmed')"
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
</template>
