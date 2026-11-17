<template>
  <NuxtLink
    :to="to"
    class="group block rounded-lg outline-none focus-visible:ring-2 focus-visible:ring-ring"
  >
    <AppCard class="h-full transition-colors group-hover:border-border-strong">
      <div class="flex items-center gap-2 text-sm text-muted-foreground">
        <AppIcon
          :icon="icon"
          size="sm"
        />
        <span class="truncate">{{ label }}</span>
      </div>
      <div class="mt-3 text-2xl leading-none font-semibold tracking-tight text-foreground tabular-nums">
        <AppSkeleton
          v-if="count.loading"
          class="h-6 w-10"
        />
        <template v-else>{{ count.value }}{{ count.more ? '+' : '' }}</template>
      </div>
      <p
        class="mt-2 flex items-center gap-1 text-xs text-muted-foreground transition-colors group-hover:text-foreground"
      >
        {{ hint }}
        <AppIcon
          :icon="ArrowRight"
          size="xs"
        />
      </p>
    </AppCard>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { ArrowRight } from '@lucide/vue'
import type { HomeCount } from '../composables/useHomeOverview'

defineProps<{ label: string; hint: string; icon: Component; count: HomeCount; to: RouteLocationRaw }>()
</script>
