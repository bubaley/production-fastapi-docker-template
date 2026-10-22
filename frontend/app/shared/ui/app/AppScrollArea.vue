<script setup lang="ts">
import { ScrollArea } from '~/shared/ui/shadcn/scroll-area'
</script>

<template>
  <!-- Thin, theme-colored scrollbars that stay consistent across platforms. Give the area a height. -->
  <ScrollArea class="min-h-0">
    <slot />
  </ScrollArea>
</template>
