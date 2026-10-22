<script setup lang="ts">
import { computed } from 'vue'
import AppSelect from '../AppSelect.vue'
import AppInput from '../AppInput.vue'
import AppDataLabel from '../AppDataLabel.vue'
import type { AppControlSize } from '../types/control'
import type { AppLabelConfig } from '../types/label-types'
import type { FilterValue, ViewFilterField, ViewFilters, ViewFixedField } from './types'
import { filterIcon } from './filterPresentation'
import { conditionRows, supportsDateRange, writeCondition } from './filterConditions'
import ViewFilterDateValue from './ViewFilterDateValue.vue'
import ViewBooleanFilter from './ViewBooleanFilter.vue'
import ViewFilterCondition from './ViewFilterCondition.vue'
const props = withDefaults(
  defineProps<{
    field: ViewFilterField
    config: ViewFixedField
    selectedItems?: object[]
    locale?: 'ru' | 'en'
    size?: AppControlSize
    disabled?: boolean
  }>(),
  { locale: 'ru', size: 'default' }
)
const model = defineModel<ViewFilters>({ required: true })
const optionalRow = computed(() => conditionRows([props.field], model.value)[0])
const entry = computed(() =>
  Object.entries(model.value).find(([key]) => {
    if (key.split('__')[0] !== props.field.field) return false
    return (
      props.config.mode === 'optional' ||
      (props.config.mode === 'multiple'
        ? key === `${props.field.field}__in`
        : key === props.field.field || key === `${props.field.field}__exact`)
    )
  })
)
const lookup = computed(() =>
  props.config.mode === 'optional'
    ? (optionalRow.value?.lookup ?? (supportsDateRange(props.field) ? 'range' : props.field.lookups[0] || 'exact'))
    : entry.value?.[0].split('__')[1] || (entry.value ? 'exact' : props.field.lookups[0] || 'exact')
)
const value = computed(() => {
  const raw = entry.value?.[1]
  if (props.config.mode === 'optional') return optionalRow.value?.value ?? ''
  if (lookup.value !== 'exact' && lookup.value !== 'in') return props.config.mode === 'multiple' ? [] : null
  return props.config.mode === 'multiple'
    ? raw == null
      ? []
      : Array.isArray(raw)
        ? raw
        : [raw]
    : Array.isArray(raw)
      ? (raw[0] ?? null)
      : (raw ?? null)
})
function set(
  value: unknown,
  operator = props.config.mode === 'multiple' ? 'in' : props.config.mode === 'single' ? 'exact' : lookup.value
) {
  if (props.config.mode === 'optional') {
    model.value = writeCondition(
      model.value,
      props.field,
      lookup.value,
      value == null || value === '' ? null : operator,
      value as FilterValue
    )
    return
  }
  const next = Object.fromEntries(Object.entries(model.value).filter(([key]) => key !== entry.value?.[0]))
  if (value != null && value !== '' && (!Array.isArray(value) || value.length)) {
    next[operator === 'exact' ? props.field.field : `${props.field.field}__${operator}`] = value as FilterValue
  }
  model.value = next
}
function changeLookup(operator: string) {
  model.value = writeCondition(model.value, props.field, lookup.value, operator, (value.value ?? '') as FilterValue)
}
const lookups = computed(() => [...(supportsDateRange(props.field) ? ['range'] : []), ...props.field.lookups])
function appearance(item: unknown) {
  return (item as { appearance?: AppLabelConfig } | undefined)?.appearance
}
</script>
<template>
  <ViewBooleanFilter
    v-if="field.kind === 'boolean' && config.mode !== 'optional'"
    :model-value="typeof value === 'boolean' ? value : null"
    :label="field.label"
    :clearable="config.clearable !== false"
    :disabled="disabled"
    :locale="locale"
    :size="size"
    @update:model-value="set($event, 'exact')"
  />
  <ViewFilterCondition
    v-else-if="config.mode === 'optional'"
    :field="field"
    :model-value="(value ?? '') as FilterValue"
    :lookup="lookup"
    :lookups="lookups"
    :selected-items="selectedItems"
    inline
    :removable="config.clearable !== false"
    :clearable="config.clearable !== false"
    :disabled="disabled"
    :locale="locale"
    :size="size"
    @update:model-value="set($event)"
    @lookup="changeLookup"
    @remove="set(null)"
  />
  <AppSelect
    v-else-if="field.kind === 'choice'"
    :model-value="value as never"
    :items="field.items"
    :repo="field.repo"
    :query="field.query"
    :item-label="field.itemLabel || 'name'"
    :selected-items="selectedItems"
    :multiple="config.mode === 'multiple'"
    :clearable="config.clearable !== false"
    emit-value
    :icon="filterIcon(field)"
    hide-dropdown-icon
    :placeholder="field.label"
    :aria-label="field.label"
    :locale="locale"
    :size="size"
    :disabled="disabled"
    class="shrink-0"
    @update:model-value="set($event)"
  >
    <template #item="{ item, label }">
      <AppDataLabel
        v-if="appearance(item)"
        :config="appearance(item)!"
      /><span v-else>{{ label }}</span>
    </template>
  </AppSelect>
  <ViewFilterDateValue
    v-else-if="field.kind === 'date' || field.kind === 'datetime'"
    :field="field"
    :lookup="lookup"
    :model-value="(value ?? '') as FilterValue"
    :size="size"
    :locale="locale"
    :disabled="disabled"
    @update:model-value="set($event)"
  />
  <AppInput
    v-else
    :model-value="String(value ?? '')"
    :icon="filterIcon(field)"
    :placeholder="field.label"
    :aria-label="field.label"
    :clearable="config.clearable !== false"
    :size="size"
    :disabled="disabled"
    @update:model-value="set($event)"
  />
</template>
