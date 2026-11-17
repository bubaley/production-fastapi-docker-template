<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const progressTones = ['primary', 'success', 'info', 'warning', 'destructive'] as const
</script>

<template>
  <UiDemo
    title="Progress"
    code=':value tone="…"'
    description="A known share of work. Every bar needs an aria-label."
  >
    <div class="flex flex-col gap-5">
      <div
        v-for="(tone, index) in progressTones"
        :key="tone"
        class="flex items-center gap-3"
      >
        <code class="w-24 text-xs text-muted-foreground">{{ tone }}</code>
        <AppProgress
          :value="30 + index * 15"
          :tone="tone"
          :aria-label="`${tone} progress`"
        />
      </div>
      <div class="flex flex-wrap items-center gap-4 border-t border-border pt-4">
        <AppCircularProgress :value="68" />
        <AppCircularProgress
          :value="40"
          tone="success"
        />
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Loading"
    code="AppLoadingIndicator label · AppSkeleton :lines circle"
    description="A spinner for a short wait in place; a skeleton in place of content that keeps its shape."
  >
    <div class="flex flex-col gap-4">
      <AppLoadingIndicator label="Loading data…" />
      <div class="flex items-center gap-3 border-t border-border pt-4">
        <AppSkeleton circle />
        <div class="w-48"><AppSkeleton :lines="2" /></div>
      </div>
      <AppSkeleton :lines="3" />
    </div>
  </UiDemo>
</template>
