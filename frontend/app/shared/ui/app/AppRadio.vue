<script setup lang="ts">
import { computed, useAttrs, useId } from 'vue'

defineOptions({ inheritAttrs: false })
defineProps<{ label?: string; val?: unknown; disable?: boolean; disabled?: boolean }>()
const model = defineModel<any>()
const attrs = useAttrs()
const generatedId = useId()
const id = computed(() => (typeof attrs.id === 'string' ? attrs.id : generatedId))
</script>

<template>
  <label
    :for="id"
    class="inline-flex cursor-pointer items-center gap-2 text-sm"
  >
    <input
      :id="id"
      v-bind="attrs"
      v-model="model"
      type="radio"
      :value="val"
      :disabled="disable || disabled"
      class="size-4 border-input accent-primary focus-visible:ring-2 focus-visible:ring-ring"
    >
    <slot>{{ label }}</slot>
  </label>
</template>
