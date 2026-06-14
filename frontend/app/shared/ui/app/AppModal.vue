<template>
  <Dialog
    v-model:visible="model"
    :style="{ width: width }"
    :show-header="showHeader"
    :dismissable-mask="dismissableMask"
    :modal="modal"
    content-class="!p-4"
    v-bind="$attrs"
  >
    <AppTitle
      v-if="title || subtitle"
      class="mb-4"
      :title="title"
      :size="titleSize"
      :subtitle="subtitle"
    />
    <slot />
  </Dialog>
</template>

<script setup lang="ts">
import type { DialogProps } from 'primevue/dialog'

export interface AppModalProps extends DialogProps {
  title?: string
  subtitle?: string
  width?: string
  titleSize?: TitleSizeToken
}

const model = defineModel<boolean>()
withDefaults(defineProps<AppModalProps>(), {
  width: '25rem',
  modal: true,
  showFooter: false,
  showHeader: false,
  dismissableMask: true,
  titleSize: 'lg',
})
</script>
