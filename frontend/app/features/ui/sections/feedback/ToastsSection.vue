<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
</script>

<template>
  <UiDemo
    title="Default and error"
    code="toast.default(title, { description }) · toast.error(…)"
    description="Short past-tense title of what happened; description only when it adds something."
  >
    <div class="flex flex-wrap items-center gap-3">
      <AppButton
        variant="outline"
        label="Default toast"
        @click="toast.default('Changes saved', { description: 'You can continue working.' })"
      />
      <AppButton
        variant="outline"
        label="Error toast"
        @click="toast.error('Could not save', { description: 'Please try again.' })"
      />
    </div>
  </UiDemo>
</template>
