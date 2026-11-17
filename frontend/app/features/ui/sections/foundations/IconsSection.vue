<script setup lang="ts">
import { Bell, Building2, CalendarDays, House, Search, Settings, Users } from '@lucide/vue'
import type { AppIconSize } from '~/shared/ui/app/AppIcon.vue'
import type { Tone } from '~/shared/ui/app/tone'
import UiDemo from '../../components/UiDemo.vue'

const sizes: AppIconSize[] = ['xs', 'sm', 'md', 'lg']
const tones: Tone[] = ['neutral', 'muted', 'primary', 'success', 'info', 'warning', 'destructive']
const icons = [House, Building2, Users, Settings, Search, Bell, CalendarDays]
</script>

<template>
  <UiDemo
    title="Sizes"
    code='size="xs | sm | md | lg" · :size="24"'
    description="12, 14, 16 and 20px; md matches body text. A number sets any other pixel size."
  >
    <div class="flex flex-wrap items-end gap-8">
      <div
        v-for="size in sizes"
        :key="size"
        class="flex flex-col items-center gap-2"
      >
        <AppIcon
          :icon="House"
          :size="size"
        />
        <code class="text-xs text-muted-foreground">{{ size }}</code>
      </div>
      <div class="flex flex-col items-center gap-2">
        <AppIcon
          :icon="House"
          :size="24"
        />
        <code class="text-xs text-muted-foreground">24</code>
      </div>
    </div>
  </UiDemo>

  <UiDemo
    title="Tones"
    code='tone="muted"'
    description="Icons take the text color by default; a tone colors one only when the color carries meaning."
  >
    <div class="flex flex-wrap gap-6">
      <div
        v-for="(tone, index) in tones"
        :key="tone"
        class="flex flex-col items-center gap-2"
      >
        <AppIcon
          :icon="icons[index]"
          :tone="tone"
          size="lg"
        />
        <code class="text-xs text-muted-foreground">{{ tone }}</code>
      </div>
    </div>
  </UiDemo>

  <UiDemo
    title="Loading and labels"
    code='loading · label="…"'
    description="loading swaps the icon for a spinner. An icon is decorative (aria-hidden) unless it gets a label, then it is announced as an image."
  >
    <div class="flex flex-wrap items-center gap-6 text-sm">
      <span class="inline-flex items-center gap-2"><AppIcon loading /> Saving…</span>
      <span class="inline-flex items-center gap-2">
        <AppIcon
          :icon="Bell"
          label="Notifications"
        />
        With an accessible name
      </span>
    </div>
  </UiDemo>
</template>
