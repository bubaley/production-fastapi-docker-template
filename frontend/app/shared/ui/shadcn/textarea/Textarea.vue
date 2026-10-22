<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '~/shared/lib/utils'
defineOptions({ inheritAttrs: false })
const props = defineProps<{ class?: HTMLAttributes['class'] }>()
const model = defineModel<string>({ default: '' })
</script>
<template>
  <textarea
    v-bind="$attrs"
    v-model="model"
    :class="
      cn(
        'min-h-24 w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground shadow-sm transition-colors outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )
    "
  />
</template>
