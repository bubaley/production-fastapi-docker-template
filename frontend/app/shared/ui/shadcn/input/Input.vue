<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '~/shared/lib/utils'

defineOptions({ inheritAttrs: false })

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    v-bind="$attrs"
    v-model="model"
    data-slot="input"
    :class="
      cn(
        'flex w-full rounded-md border border-input bg-background py-1 text-foreground shadow-sm transition-colors outline-none file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/30 enabled:hover:bg-field-hover disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )
    "
  />
</template>
