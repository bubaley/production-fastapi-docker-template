<template>
  <UiShowcaseSection
    title="Form controls"
    description="Shared inputs used across list filters and detail pages."
  >
    <UiShowcaseItem
      stacked
      :label="`AppInput: ${inputValue || 'empty'}`"
    >
      <AppInput
        v-model="inputValue"
        label="Label"
        placeholder="Enter value"
      />
      <AppInput
        v-model="searchValue"
        is-search
        clearable
        placeholder="Search"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      :label="`AppTextarea: ${textareaValue || 'empty'}`"
    >
      <AppTextarea
        v-model="textareaValue"
        auto-resize
        rows="3"
        placeholder="Enter long text"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      :label="`AppSelect: ${selectValue?.label ?? '—'}`"
    >
      <AppSelect
        v-model="selectValue"
        option-label="label"
        :options="options"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      :label="`AppMultiSelect: ${multiSelectValue.map((item) => item.label).join(', ') || '—'}`"
    >
      <AppMultiSelect
        v-model="multiSelectValue"
        option-label="label"
        :options="options"
      />
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      :label="`AppDatePicker: ${dateValue ?? 'null'}`"
    >
      <AppDatePicker v-model="dateValue" />
    </UiShowcaseItem>

    <UiShowcaseItem
      stacked
      :label="`AppColorPicker: ${colorValue}`"
    >
      <AppColorPicker v-model="colorValue" />
    </UiShowcaseItem>

    <UiShowcaseItem label="AppCheckbox">
      <AppCheckbox
        v-model="checked"
        input-id="ui-checkbox-enabled"
        label="Enabled"
      />
      <AppCheckbox
        v-model="checked"
        input-id="ui-checkbox-disabled"
        label="Disabled"
        disabled
      />
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { AppTab } from '~/shared/ui/app/AppTabs.vue'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const options = ref<AppTab[]>([
  { label: 'Home', value: 'home' },
  { label: 'About', value: 'about' },
  { label: 'Contact', value: 'contact' },
  { label: 'Empty', value: 'empty' },
])
const selectValue = ref(options.value[0])
const multiSelectValue = ref<AppTab[]>(options.value.filter((_, index) => [0, 2].includes(index)))
const inputValue = ref('')
const searchValue = ref('')
const textareaValue = ref('')
const dateValue = ref<string | null>(dayjs().format('YYYY-MM-DD'))
const colorValue = ref('#3b82f6')
const checked = ref(true)
</script>
