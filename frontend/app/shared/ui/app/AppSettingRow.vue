<script setup lang="ts">
import { useId } from 'vue'
import AppCheckbox from './AppCheckbox.vue'
defineProps<{ label: string; description?: string; disabled?: boolean }>()
const model = defineModel<boolean>({ default: false })
const id = useId()
</script>
<template>
  <div class="border-b border-border py-4 first:pt-0 last:border-0 last:pb-0">
    <AppCheckbox
      v-model="model"
      :disabled="disabled"
      :aria-describedby="description ? id : undefined"
    >
      <span class="font-medium">{{ label }}</span>
    </AppCheckbox>
    <p
      v-if="description"
      :id="id"
      class="mt-1 pl-7 text-sm leading-relaxed text-muted-foreground"
    >
      {{ description }}
    </p>
  </div>
</template>
