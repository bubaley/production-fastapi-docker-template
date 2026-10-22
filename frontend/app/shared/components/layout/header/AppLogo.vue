<template>
  <div class="flex items-center text-muted-foreground transition-colors hover:text-foreground">
    <Flame
      :size="24"
      aria-hidden="true"
    />
    <div class="ml-1.5 text-sm font-semibold sm:text-lg">FastAPI + Nuxt Template</div>
  </div>
</template>

<script setup lang="ts">
import { Flame } from '@lucide/vue'
</script>
