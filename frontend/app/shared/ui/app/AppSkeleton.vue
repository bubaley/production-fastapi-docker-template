<script setup lang="ts">
import { Skeleton } from '~/shared/ui/shadcn/skeleton'

withDefaults(defineProps<{ lines?: number }>(), { lines: 1 })
</script>

<template>
  <span
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
