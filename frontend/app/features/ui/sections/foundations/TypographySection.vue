<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const titles = [
  { size: 'xl', as: 'h1', text: 'xl · text-2xl · h1' },
  { size: 'lg', as: 'h2', text: 'lg · text-xl · h2' },
  { size: 'md', as: 'h3', text: 'md · text-base · h3' },
  { size: 'sm', as: 'h4', text: 'sm · text-sm · h4' },
] as const
const scale = [
  { name: 'text-xs', class: 'text-xs' },
  { name: 'text-control-sm', class: 'text-control-sm' },
  { name: 'text-sm (body)', class: 'text-sm' },
  { name: 'text-base (root)', class: 'text-base' },
  { name: 'text-xl', class: 'text-xl' },
  { name: 'text-3xl', class: 'text-3xl' },
]
</script>

<template>
  <UiDemo
    title="Headings"
    code='size="xl | lg | md | sm" as="h1…h4"'
    description="PageHeader uses h1/xl, AppSection h2/lg. Pick the tag by document outline, the size by weight on screen."
  >
    <div class="flex flex-col gap-4">
      <AppTitle
        v-for="sample in titles"
        :key="sample.size"
        :size="sample.size"
        :as="sample.as"
        :title="sample.text"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Type scale"
    code="text-xs … text-3xl"
    description="Tailwind sizes on a 14px root. Controls use text-control-* from their size."
  >
    <div class="flex flex-col gap-1">
      <div
        v-for="item in scale"
        :key="item.name"
        :class="item.class"
      >
        {{ item.name }}
      </div>
    </div>
  </UiDemo>
</template>
