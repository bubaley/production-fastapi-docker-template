<template>
  <UiShowcaseSection
    title="SmartDatePicker"
    description="Relative expressions (now-1h), absolute datetime, calendar and quick presets."
  >
    <UiShowcaseItem
      v-for="item in pickers"
      :key="item.key"
      stacked
      :label="item.label"
      :caption="item.caption"
    >
      <AppSmartDatePicker
        v-model="smartDates[item.key]"
        v-bind="item.props"
      />
      <div class="text-sm fg-secondary">
        value:
        <span class="font-medium fg-base">{{ smartDates[item.key] ?? 'null' }}</span>
      </div>
    </UiShowcaseItem>

    <UiShowcaseItem
      label="AppSmartDateRangePicker"
      caption="from / to range"
      stacked
    >
      <AppSmartDateRangePicker v-model="smartRange" />
      <div class="text-sm fg-secondary">
        from
        <span class="font-medium fg-base">{{ smartRange.from }}</span>
        → to
        <span class="font-medium fg-base">{{ smartRange.to }}</span>
        <template v-if="smartRange.quickRangeId">({{ smartRange.quickRangeId }})</template>
      </div>
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import {
  SMART_DATE_RANGE_DEFAULT,
  type SmartDateRange,
} from '~/shared/ui/app/smartDatePicker/composables/useSmartDateRange'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const smartDates = reactive({
  labeled: 'now-1h' as string | null,
  plain: 'now' as string | null,
})

const pickers: {
  key: keyof typeof smartDates
  label: string
  caption?: string
  props: { label?: string; placeholder: string; showQuickDates?: boolean }
}[] = [
  {
    key: 'labeled',
    label: 'AppSmartDatePicker',
    caption: 'single value',
    props: { label: 'Expression', placeholder: 'now-1h' },
  },
  {
    key: 'plain',
    label: 'Unlabeled + no quick list',
    props: { placeholder: 'now', showQuickDates: false },
  },
]

const smartRange = ref<SmartDateRange>({ ...SMART_DATE_RANGE_DEFAULT })
</script>
