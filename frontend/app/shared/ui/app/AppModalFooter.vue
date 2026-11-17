<template>
  <DialogFooter>
    <slot />
  </DialogFooter>
</template>

<script setup lang="ts">
import { provide } from 'vue'
import { DialogFooter } from '~/shared/ui/shadcn/dialog'
import { IN_MODAL_FOOTER } from './modalFooter'

provide(IN_MODAL_FOOTER, true)
</script>
