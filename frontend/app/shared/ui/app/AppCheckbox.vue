<template>
  <div
    :class="props.class"
    class="flex items-center gap-2"
  >
    <Checkbox
      v-model="model"
      :input-id="inputId"
      v-bind="{ ...$attrs, binary }"
      :readonly="!!readonly"
      :disabled="disabled"
    />
    <label
      v-if="label"
      :for="inputId"
      class="cursor-pointer"
    >
      {{ label }}
    </label>
  </div>
</template>

<script setup lang="ts">
import type { CheckboxProps } from 'primevue/checkbox'

export interface CCheckboxProps extends /* @vue-ignore */ CheckboxProps {
  label?: string
  inputId?: string
  binary?: boolean
  class?: string
  disabled?: boolean
  readonly?: boolean
}

const model = defineModel<boolean>()

const props = withDefaults(defineProps<CCheckboxProps>(), {
  inputId: 'checkbox',
  binary: true,
})
</script>
