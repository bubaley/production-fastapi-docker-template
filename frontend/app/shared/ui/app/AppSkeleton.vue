<script setup lang="ts">
import { Skeleton } from '~/shared/ui/shadcn/skeleton'

// `circle`: an avatar placeholder (2rem) instead of text lines.
withDefaults(defineProps<{ lines?: number; circle?: boolean }>(), { lines: 1 })
</script>

<template>
  <Skeleton
    v-if="circle"
    class="size-8 shrink-0 rounded-full"
    aria-hidden="true"
  />
  <span
    v-else
    class="flex w-full flex-col gap-2"
    aria-hidden="true"
  >
    <Skeleton
      v-for="line in lines"
      :key="line"
      class="h-4 w-full last:w-3/4 first:last:w-full"
    />
  </span>
</template>
