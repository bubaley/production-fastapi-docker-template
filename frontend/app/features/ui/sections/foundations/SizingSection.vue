<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const radii = [
  { name: 'rounded-sm', class: 'rounded-sm' },
  { name: 'rounded-md (--radius)', class: 'rounded-md' },
  { name: 'rounded-lg', class: 'rounded-lg' },
  { name: 'rounded-xl', class: 'rounded-xl' },
]
const controls = [
  { name: 'h-control-xs', class: 'h-control-xs' },
  { name: 'h-control-sm', class: 'h-control-sm' },
  { name: 'h-control-md', class: 'h-control-md' },
  { name: 'h-control-lg', class: 'h-control-lg' },
]
</script>

<template>
  <UiDemo
    title="Radius"
    code="rounded-sm · rounded-md · rounded-lg · rounded-xl"
    description="Controls use md, cards lg, empty states and large frames xl."
  >
    <div class="flex flex-wrap gap-6">
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
  </UiDemo>
  <UiDemo
    title="Control heights"
    code='size="xs | sm | md | lg"'
    description="One height per size for buttons, inputs, selects and switches; md is the default."
  >
    <div class="flex flex-wrap items-end gap-6">
      <div
        v-for="control in controls"
        :key="control.name"
        class="flex flex-col items-start gap-2"
      >
        <div
          class="w-20 rounded-md bg-primary"
          :class="control.class"
        />
        <code class="text-xs text-muted-foreground">{{ control.name }}</code>
      </div>
    </div>
  </UiDemo>
</template>
