<template>
  <UiShowcaseSection
    title="AppDataLabel"
    description="Field caption + value. Pass a label config as the visual template, or set icon/color directly."
  >
    <UiShowcaseItem
      v-for="row in dataLabelRows"
      :key="row.label"
      :label="row.label"
      :caption="row.caption"
    >
      <AppDataLabel
        v-for="item in row.items"
        :key="item.config?.label ?? item.label"
        v-bind="bindDataLabel(item)"
      >
        <AppDateLabel
          v-if="item.dateType"
          :type="item.dateType"
          :date="now"
        />
      </AppDataLabel>
    </UiShowcaseItem>

    <UiShowcaseItem label="Slots">
      <AppDataLabel
        label="Role"
        value="Owner"
        icon="lucide:shield"
        color="success"
      >
        <template #label-append>
          <AppLabel
            label="default"
            icon="lucide:star"
            color="orange"
          />
        </template>
        <template #label-tooltip> Organization-level access. Owners can manage members and billing. </template>
      </AppDataLabel>
    </UiShowcaseItem>
  </UiShowcaseSection>

  <UiShowcaseSection
    title="AppLabel"
    description="Compact status chip: icon + text, or either part alone."
    class="mt-6"
  >
    <UiShowcaseItem
      v-for="row in labelModeRows"
      :key="row.label"
      :label="row.label"
      :caption="row.caption"
    >
      <AppLabel
        v-for="item in labels"
        :key="`${row.label}-${item.label}`"
        v-bind="item"
        :mode="row.mode"
      />
    </UiShowcaseItem>

    <UiShowcaseItem label="AppDateLabel">
      <template
        v-for="type in dateTypes"
        :key="type"
      >
        <span class="text-sm fg-secondary">{{ type }}</span>
        <AppDateLabel
          :type="type"
          :date="now"
        />
      </template>
    </UiShowcaseItem>

    <UiShowcaseItem
      label="DurationLabel"
      stacked
    >
      <div class="flex flex-wrap items-end gap-3">
        <AppSelect
          v-model="durationFormat"
          label="format"
          option-label="label"
          option-value="value"
          :options="durationFormatOptions"
        />
        <AppMultiSelect
          v-model="durationUnits"
          label="units"
          option-label="label"
          option-value="value"
          :options="durationUnitOptions"
        />
        <DurationLabel
          class="radius-full bg-tertiary px-1.5 py-0.5 text-sm leading-none fg-secondary"
          :date="durationDate"
          :format="durationFormat"
          :units="durationUnits"
        />
      </div>
      <div class="flex flex-wrap items-center gap-2 text-sm">
        <template
          v-for="example in durationExamples"
          :key="example.caption"
        >
          <span class="fg-secondary">{{ example.caption }}</span>
          <DurationLabel
            :date="durationDate"
            :format="example.format"
            :units="example.units"
            :unit="example.unit"
          />
        </template>
      </div>
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import DurationLabel from '~/shared/components/labels/DurationLabel.vue'
import type { DurationFormat, DurationUnit } from '~/shared/components/labels/DurationLabel.vue'
import type { AppDataLabelProps } from '~/shared/ui/app/AppDataLabel.vue'
import type { DateType } from '~/shared/composables/useDate'
import type { AppLabelConfig } from '~/shared/ui/app/types/label-types'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const now = dayjs().toISOString()
const durationDate = dayjs().subtract(123, 'hour').subtract(23, 'minute').subtract(53, 'second').toISOString()
const durationFormat = ref<DurationFormat>('clock')
const durationUnits = ref<DurationUnit[]>(['hours', 'minutes'])
const dateTypes: DateType[] = ['date', 'datetime']

const durationFormatOptions: { label: string; value: DurationFormat }[] = [
  { label: 'clock — 00:23', value: 'clock' },
  { label: 'parts — 123ч 23м', value: 'parts' },
  { label: 'value — 523231с', value: 'value' },
]
const durationUnitOptions: { label: string; value: DurationUnit }[] = [
  { label: 'hours', value: 'hours' },
  { label: 'minutes', value: 'minutes' },
  { label: 'seconds', value: 'seconds' },
]

const durationExamples: { caption: string; format: DurationFormat; units?: DurationUnit[]; unit?: DurationUnit }[] = [
  { caption: 'clock h:m', format: 'clock', units: ['hours', 'minutes'] },
  { caption: 'clock m:s', format: 'clock', units: ['minutes', 'seconds'] },
  { caption: 'clock h:m:s', format: 'clock', units: ['hours', 'minutes', 'seconds'] },
  { caption: 'parts h m', format: 'parts', units: ['hours', 'minutes'] },
  { caption: 'value / seconds', format: 'value', unit: 'seconds' },
]

const labels: AppLabelConfig[] = [
  { label: 'Active', icon: 'lucide:circle-check', color: 'success' },
  { label: 'Pending', icon: 'lucide:clock', color: 'orange' },
  { label: 'Failed', icon: 'lucide:circle-x', color: 'danger' },
  { label: 'Info', icon: 'lucide:info', color: 'info' },
  { label: 'Draft', icon: 'lucide:file', color: 'secondary' },
  { label: 'Primary', icon: 'lucide:star', color: 'primary' },
]

const labelModeRows: { label: string; caption?: string; mode?: 'icon' | 'label' }[] = [
  { label: 'Default' },
  { label: 'Icon only', caption: 'mode=icon', mode: 'icon' },
  { label: 'Text only', caption: 'mode=label', mode: 'label' },
]

type DataLabelDemo = AppDataLabelProps & { dateType?: DateType }

const bindDataLabel = ({ dateType: _dateType, ...props }: DataLabelDemo) => props

const dataLabelRows: { label: string; caption?: string; items: DataLabelDemo[] }[] = [
  {
    label: 'Basic',
    items: [
      { label: 'Email', value: 'ada@example.com', icon: 'lucide:mail', color: 'primary' },
      { label: 'Organization', value: 'Acme Inc.', icon: 'lucide:building-2', color: 'secondary' },
      { label: 'Created', icon: 'lucide:calendar', color: 'info', dateType: 'date' },
    ],
  },
  {
    label: 'From config',
    caption: 'icon, color and fallback value',
    items: labels.map((config) => ({ label: 'Status', config })),
  },
  {
    label: 'Size xl',
    caption: 'size=xl',
    items: [{ size: 'xl', label: 'Plan', value: 'Production', icon: 'lucide:gem', color: 'pink' }],
  },
  {
    label: 'Link, copy, empty',
    items: [
      {
        label: 'Profile',
        value: 'Open settings',
        icon: 'lucide:user',
        color: 'primary',
        to: { name: 'settings-profile' },
      },
      { label: 'API token', value: 'sk_live_demo_token', icon: 'lucide:key', color: 'orange', copied: true },
      { label: 'Phone', icon: 'lucide:phone', color: 'secondary' },
    ],
  },
]
</script>
