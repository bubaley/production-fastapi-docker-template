<template>
  <UiShowcaseSection
    title="AppButton"
    description="PrimeVue button wrapper with loading, icons, routing and severity variants."
  >
    <UiShowcaseItem
      v-for="row in variantRows"
      :key="row.label"
      :label="row.label"
      :caption="row.caption"
    >
      <AppButton
        v-for="severity in severities"
        :key="severity"
        :label="severity"
        :severity="severity"
        :variant="row.variant"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      v-for="row in buttonRows"
      :key="row.label"
      :label="row.label"
    >
      <AppButton
        v-for="(item, index) in row.items"
        :key="index"
        v-bind="item"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      label="AppTextButton"
      caption="Inline text action"
    >
      <AppTextButton
        v-for="severity in textColors"
        :key="severity"
        :label="severity"
        :severity="severity"
      />
      <AppTextButton
        label="With icon"
        icon="lucide:external-link"
        severity="primary"
      />
      <AppTextButton
        label="No underline"
        :underline="false"
        severity="secondary"
      />
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import type { AppButtonProps } from '~/shared/ui/app/AppButton.vue'
import type { ColorToken } from '~/shared/ui/template/types/template-ui-tokens'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const severities: NonNullable<AppButtonProps['severity']>[] = [
  'primary',
  'secondary',
  'success',
  'info',
  'warn',
  'danger',
  'contrast',
]

const textColors: ColorToken[] = ['primary', 'secondary', 'info', 'success', 'danger', 'orange', 'teal', 'pink']

const variantRows: { label: string; caption?: string; variant?: AppButtonProps['variant'] }[] = [
  { label: 'Severity' },
  { label: 'Outlined', caption: 'variant=outlined', variant: 'outlined' },
  { label: 'Text', caption: 'variant=text', variant: 'text' },
]

type DemoButton = {
  label?: string
  icon?: string
  iconPos?: 'left' | 'right'
  size?: AppButtonProps['size']
  severity?: AppButtonProps['severity']
  variant?: AppButtonProps['variant']
  rounded?: boolean
  loading?: boolean
  disabled?: boolean
}

const buttonRows: { label: string; items: DemoButton[] }[] = [
  {
    label: 'Size',
    items: [
      { label: 'Small', size: 'small', icon: 'lucide:plus' },
      { label: 'Default', icon: 'lucide:plus' },
      { label: 'Large', size: 'large', icon: 'lucide:plus' },
    ],
  },
  {
    label: 'Icons',
    items: [
      { label: 'Left icon', icon: 'lucide:settings' },
      { label: 'Right icon', icon: 'lucide:arrow-right', iconPos: 'right', severity: 'secondary' },
      { icon: 'lucide:pencil' },
      { icon: 'lucide:trash-2', severity: 'danger', variant: 'outlined' },
      { rounded: true, icon: 'lucide:plus' },
    ],
  },
  {
    label: 'States',
    items: [
      { label: 'Loading', icon: 'lucide:save', loading: true },
      { label: 'Disabled', disabled: true },
      { label: 'Rounded', rounded: true, severity: 'success' },
    ],
  },
]
</script>
