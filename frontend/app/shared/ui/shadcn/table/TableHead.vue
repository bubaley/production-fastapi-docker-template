<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '~/shared/lib/utils'
const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>
<template>
  <th :class="cn('h-10 px-4 text-left align-middle text-base font-medium text-muted-foreground', props.class)">
    <slot />
  </th>
</template>
