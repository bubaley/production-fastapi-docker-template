<script setup lang="ts">
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
const charts = ['bg-chart-1', 'bg-chart-2', 'bg-chart-3', 'bg-chart-4', 'bg-chart-5']
const radii = [
  { name: 'sm', class: 'rounded-sm' },
  { name: 'md (--radius)', class: 'rounded-md' },
  { name: 'lg', class: 'rounded-lg' },
  { name: 'xl', class: 'rounded-xl' },
]
const controls = [
  { name: 'control-xs', class: 'h-control-xs' },
  { name: 'control-sm', class: 'h-control-sm' },
  { name: 'control-md', class: 'h-control-md' },
  { name: 'control-lg', class: 'h-control-lg' },
]
const text = [
  { name: 'text-xs', class: 'text-xs' },
  { name: 'text-control-sm', class: 'text-control-sm' },
  { name: 'text-sm', class: 'text-sm' },
  { name: 'text-base (root)', class: 'text-base' },
  { name: 'text-xl', class: 'text-xl' },
  { name: 'text-3xl', class: 'text-3xl' },
]
</script>
<template>
  <div class="space-y-10">
    <AppSection
      title="Color tokens"
      description="Defined once in assets/styles/theme.css; switch theme and palette at the top to compare."
    >
      <AppCard class="space-y-5">
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
      </AppCard>
    </AppSection>
    <AppSection
      title="Radius, controls and type"
      description="Radii derive from --radius; control heights from --size-control-*; the rem base is 87.5% (14px)."
    >
      <AppCard class="grid gap-6 md:grid-cols-3">
        <div class="space-y-2">
          <div
            v-for="radius in radii"
            :key="radius.name"
            class="flex items-center gap-3"
          >
            <div
              class="size-10 border border-border-strong bg-muted"
              :class="radius.class"
            />
            <code class="text-xs text-muted-foreground">{{ radius.name }}</code>
          </div>
        </div>
        <div class="space-y-2">
          <div
            v-for="control in controls"
            :key="control.name"
            class="flex items-center gap-3"
          >
            <div
              class="w-16 rounded-md bg-primary"
              :class="control.class"
            />
            <code class="text-xs text-muted-foreground">{{ control.name }}</code>
          </div>
        </div>
        <div class="space-y-1">
          <div
            v-for="item in text"
            :key="item.name"
            :class="item.class"
          >
            {{ item.name }}
          </div>
        </div>
      </AppCard>
    </AppSection>
  </div>
</template>
