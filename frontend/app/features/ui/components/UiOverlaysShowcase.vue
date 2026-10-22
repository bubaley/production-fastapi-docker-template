<script setup lang="ts">
const toast = useToast()
const modal = ref(false)
const confirm = ref(false)
const drawer = ref(false)
const unsaved = ref(false)
const modalName = ref('Working project')
const color = ref<string | null>('#7779ed')
const icon = ref<string | null>('folder')
const actions = [
  { label: 'Open modal', icon: 'lucide:panels-top-left', action: () => { modal.value = true } },
  { label: 'Rename', icon: 'lucide:pencil', action: () => toast.default('Rename requested') },
  { label: 'Delete', icon: 'lucide:trash-2', destructive: true, separatorBefore: true, action: () => { confirm.value = true } },
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
            { label: 'Open Modal', icon: 'lucide:panels-top-left', action: () => { modal = true } },
            { label: 'Confirmation', variant: 'outline', action: () => { confirm = true } },
            { label: 'Drawer', variant: 'outline', action: () => { drawer = true } },
            { label: 'Unsaved changes', variant: 'outline', action: () => { unsaved = true } },
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
                icon="lucide:ellipsis"
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
      <template #footer><AppTemplateActions :actions="[{ label: 'Cancel', variant: 'secondary', action: () => { modal = false } }, { label: 'Save', action: () => { toast.default('Changes saved'); modal = false } }]" /></template>
    </AppModal>
    <AppConfirmModal
      v-model="confirm"
      decline-text="Cancel"
      close-label="Close"
      title="Delete project?"
      subtitle="This is a demo. Your data will not change."
      confirm-text="Delete"
      :confirm-props="{ variant: 'destructive' }"
      :confirm="() => { toast.default('Action confirmed') }"
    />
    <AppUnsavedChangesModal
      v-model="unsaved"
      title="Save changes?"
      description="You have unsaved changes."
      save-label="Save"
      discard-label="Discard"
      cancel-label="Cancel"
      close-label="Close"
      @save="toast.default('Changes saved'); unsaved = false"
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
