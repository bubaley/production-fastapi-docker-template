<template>
  <span class="inline-flex items-center gap-1.5 whitespace-nowrap">
    <AppIcon
      v-if="mode !== 'label'"
      :icon="icon"
      :color="color"
    />
    <span v-if="mode !== 'icon'">{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
import type { AppLabelConfig } from '~/shared/ui/app/types/label-types'

defineProps<
  Pick<AppLabelConfig, 'icon' | 'label' | 'color'> & {
    mode?: 'icon' | 'label'
  }
>()
</script>
