<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
const drawer = ref(false)
const modal = ref(false)
</script>

<template>
  <UiDemo
    title="Side drawer"
    code='AppDrawer v-model side="right" :width="360"'
    description="Secondary settings without leaving the page. A date picker or a modal opened inside stacks above the drawer and keeps it open."
  >
    <AppButton
      variant="outline"
      label="Open drawer"
      @click="drawer = true"
    />
  </UiDemo>
  <AppDrawer
    v-model="drawer"
    close-label="Close"
    description="Additional settings and actions."
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
        label="Open nested modal"
        @click="modal = true"
      />
    </AppSection>
  </AppDrawer>
  <AppModal
    v-model="modal"
    close-label="Close"
    title="Nested modal"
    description="Opened from the drawer; closing it returns to the drawer."
  >
    <AppInput
      label="Name"
      model-value="Working project"
    />
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
</template>
