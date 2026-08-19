<template>
  <UiShowcaseSection
    title="AppIcon"
    description="Nuxt Icon wrapper with token colors, sizes, loading spinner and gradient fills."
  >
    <UiShowcaseItem
      v-for="row in rows"
      :key="row.label"
      :label="row.label"
      :caption="row.caption"
    >
      <template
        v-for="item in row.items"
        :key="item.key"
      >
        <div
          v-if="row.chip"
          class="flex items-center gap-2 rounded-md border border-base px-2.5 py-1.5"
        >
          <AppIcon v-bind="item.props" />
          <span class="text-xs fg-secondary">{{ item.key }}</span>
        </div>
        <AppIcon
          v-else
          v-bind="item.props"
        />
      </template>
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import type { AppIconGradientSeverity } from '~/shared/ui/app/utils/iconGradients'
import type { ColorToken } from '~/shared/ui/template/types/template-ui-tokens'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const sizes = [16, 20, 24, 32, 40]
const colors: ColorToken[] = ['primary', 'secondary', 'info', 'success', 'danger', 'orange', 'yellow', 'teal', 'pink']
const gradients: AppIconGradientSeverity[] = ['purple', 'pink', 'orange', 'green', 'blue', 'cyan', 'red']
const setIcons: { icon: string; color: ColorToken; loading?: boolean }[] = [
  { icon: 'lucide:loader', color: 'primary', loading: true },
  { icon: 'lucide:home', color: 'secondary' },
  { icon: 'lucide:bell', color: 'info' },
  { icon: 'lucide:circle-check', color: 'success' },
  { icon: 'lucide:triangle-alert', color: 'danger' },
  { icon: 'lucide:star', color: 'orange' },
]

const rows = [
  {
    label: 'Sizes',
    caption: '16 → 40',
    chip: false,
    items: sizes.map((size) => ({ key: String(size), props: { icon: 'lucide:sparkles', size, color: 'primary' as const } })),
  },
  {
    label: 'Colors',
    chip: true,
    items: colors.map((color) => ({ key: color, props: { icon: 'lucide:hexagon', color } })),
  },
  {
    label: 'Gradients',
    caption: 'gradientSeverity',
    chip: true,
    items: gradients.map((gradientSeverity) => ({
      key: gradientSeverity,
      props: { icon: 'lucide:zap', size: 22, gradientSeverity },
    })),
  },
  {
    label: 'States & set',
    chip: false,
    items: setIcons.map((props) => ({ key: props.icon, props })),
  },
]
</script>
