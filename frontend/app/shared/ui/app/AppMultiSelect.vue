<script setup lang="ts" generic="T">
import AppSelect from './AppSelect.vue'
import type { AppSelectProps } from './select/types'
const props = defineProps<AppSelectProps<T>>()
const model = defineModel<any[]>()
</script>
<template>
  <AppSelect
    v-bind="props"
    v-model="model"
    multiple
  >
    <template
      v-for="(_, name) in $slots"
      #[name]="slotProps"
    >
      <slot
        :name="name"
        v-bind="slotProps"
      />
    </template>
  </AppSelect>
</template>
