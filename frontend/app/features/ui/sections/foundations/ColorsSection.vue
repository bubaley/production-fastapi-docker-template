<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

// Literal class names so Tailwind generates every swatch.
const surfaces = [
  { name: 'background', class: 'bg-background' },
  { name: 'card', class: 'bg-card' },
  { name: 'popover', class: 'bg-popover' },
  { name: 'secondary / muted', class: 'bg-muted' },
  { name: 'accent', class: 'bg-accent' },
  { name: 'field-hover', class: 'bg-field-hover' },
  { name: 'row-hover', class: 'bg-row-hover' },
  { name: 'sidebar', class: 'bg-sidebar' },
  { name: 'border', class: 'bg-border' },
  { name: 'border-strong', class: 'bg-border-strong' },
]
const tones = [
  { name: 'primary', class: 'bg-primary text-primary-foreground' },
  { name: 'success', class: 'bg-success text-success-foreground' },
  { name: 'info', class: 'bg-info text-info-foreground' },
  { name: 'warning', class: 'bg-warning text-warning-foreground' },
  { name: 'destructive', class: 'bg-destructive text-destructive-foreground' },
  { name: 'ring', class: 'bg-ring text-background' },
]
const contrast = [
  { name: 'contrast', class: 'bg-contrast text-contrast-foreground' },
  { name: 'contrast-hover', class: 'bg-contrast-hover text-contrast-foreground' },
]
const text = [
  { name: 'text-foreground', class: 'text-foreground' },
  { name: 'text-muted-foreground', class: 'text-muted-foreground' },
  { name: 'text-primary', class: 'text-primary' },
  { name: 'text-destructive', class: 'text-destructive' },
]
const charts = ['bg-chart-1', 'bg-chart-2', 'bg-chart-3', 'bg-chart-4', 'bg-chart-5']
</script>

<template>
  <UiDemo
    title="Surfaces and borders"
    code="bg-background · bg-card · bg-muted · border-border"
    description="Neutral surfaces follow the theme; the palette only changes primary and ring."
  >
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-5">
      <div
        v-for="token in surfaces"
        :key="token.name"
        class="space-y-1"
      >
        <div
          class="h-12 rounded-md border border-border"
          :class="token.class"
        />
        <code class="text-xs text-muted-foreground">{{ token.name }}</code>
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Semantic tones"
    code='tone="primary | success | info | warning | destructive"'
    description="Status colors. Components take tone instead of a color class; see tone.ts."
  >
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-6">
      <div
        v-for="token in tones"
        :key="token.name"
        class="flex h-12 items-center justify-center rounded-md text-xs font-medium"
        :class="token.class"
      >
        {{ token.name }}
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Contrast"
    code="bg-contrast · text-contrast-foreground · bg-contrast-hover"
    description="The theme's highest-contrast fill: near-black in light, near-white in dark, the same in every palette. The default button, active chips, a selected segment and tooltips use it; primary stays the brand accent."
  >
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-6">
      <div
        v-for="token in contrast"
        :key="token.name"
        class="flex h-12 items-center justify-center rounded-md text-xs font-medium"
        :class="token.class"
      >
        {{ token.name }}
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Text"
    code="text-foreground · text-muted-foreground"
    description="Body text is foreground; captions, hints and field labels are muted."
  >
    <div class="flex flex-col gap-1">
      <span
        v-for="item in text"
        :key="item.name"
        class="text-sm"
        :class="item.class"
        >{{ item.name }}</span
      >
    </div>
  </UiDemo>
  <UiDemo
    title="Theme and palette"
    code='AppThemeSwitcher locale="en" · hide-palette'
    description="The user's theme and accent, stored in cookies. It lives in the account menu (and in this sidebar); a fork rarely needs another place for it."
  >
    <AppThemeSwitcher
      locale="en"
      class="max-w-xs"
    />
  </UiDemo>
  <UiDemo
    title="Charts"
    code="bg-chart-1 … bg-chart-5"
    description="Series colors for charts only, in this order."
  >
    <div class="flex gap-2">
      <div
        v-for="(chart, index) in charts"
        :key="chart"
        class="flex h-8 flex-1 items-center justify-center rounded-md text-xs text-background"
        :class="chart"
      >
        chart-{{ index + 1 }}
      </div>
    </div>
  </UiDemo>
</template>
