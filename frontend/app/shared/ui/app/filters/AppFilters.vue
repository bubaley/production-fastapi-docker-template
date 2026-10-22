<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFilterSelectedItems } from './useFilterSelectedItems'
import { Plus } from '@lucide/vue'
import AppIcon from '~/shared/ui/app/AppIcon.vue'
import { conditionRows, supportsDateRange, writeCondition } from './filterConditions'
import { filterIcon } from './filterPresentation'
import ViewFilterCondition from './ViewFilterCondition.vue'
import AppSelect from '~/shared/ui/app/AppSelect.vue'
import type { FilterValue, ViewFilters, ViewFilterField, ViewFilterSpec } from './types'
import { appControlIconSize, appControlStyles } from '~/shared/ui/app/types/control'
import type { AppControlSize } from '../types/control'
const props = withDefaults(
  defineProps<{
    spec: ViewFilterSpec
    lockedFilters?: ViewFilters
    locale?: 'ru' | 'en'
    inline?: boolean
    disabled?: boolean
    excludedKeys?: string[]
    wrap?: boolean
    showAdd?: boolean
    alwaysShowAdd?: boolean
    includeQuick?: boolean
    size?: AppControlSize
  }>(),
  {
    lockedFilters: () => ({}),
    locale: 'ru',
    size: 'default',
    showAdd: true
  }
)
const model = defineModel<ViewFilters>({ required: true })
const selectedItems = useFilterSelectedItems(() => props.spec, model)
const addOpen = ref(false)
const english = computed(() => props.locale === 'en')
const fields = computed(() =>
  props.spec.fields.filter(
    (field) =>
      (props.includeQuick || !field.quick) &&
      !Object.keys(props.lockedFilters).some((key) => key.split('__')[0] === field.field)
  )
)
const conditions = computed(() =>
  conditionRows(
    fields.value,
    Object.fromEntries(Object.entries(model.value).filter(([key]) => !props.excludedKeys?.includes(key)))
  )
)
function remove(key: string) {
  const row = conditions.value.find((row) => row.key === key)
  if (row) model.value = writeCondition(model.value, row.field, row.lookup, null)
}
function set(key: string, value: unknown) {
  const row = conditions.value.find((row) => row.key === key)
  if (row)
    model.value = writeCondition(
      model.value,
      row.field,
      row.lookup,
      value == null || value === '' ? null : row.lookup,
      value as FilterValue
    )
}
function replace(key: string, field: ViewFilterField, lookup: string) {
  const row = conditions.value.find((row) => row.key === key)
  model.value = writeCondition(model.value, field, row?.lookup ?? lookup, lookup, row?.value)
}
function availableLookups(field: ViewFilterField, currentKey = '') {
  return [...(supportsDateRange(field) ? ['range'] : []), ...field.lookups].filter((lookup) => {
    if (lookup === 'range')
      return (
        currentKey === `${field.field}__gte` ||
        (!(`${field.field}__gte` in model.value) && !(`${field.field}__lte` in model.value))
      )
    const key = lookup === 'exact' ? field.field : `${field.field}__${lookup}`
    if (props.excludedKeys?.includes(key) || (lookup === 'exact' && props.excludedKeys?.includes(`${field.field}__exact`))) return false
    const current = conditions.value.find((row) => row.key === currentKey)
    return (
      key === currentKey || (current?.lookup === 'range' && ['gte', 'lte'].includes(lookup)) || !(key in model.value)
    )
  })
}
function add(fieldName: unknown) {
  if (!props.showAdd || props.disabled) return
  const field = fields.value.find((field) => field.field === fieldName)
  const available = field ? availableLookups(field) : []
  const lookup = field && (props.inline && field.kind === 'choice' && available.includes('in') ? 'in' : available[0])
  if (field && lookup) replace('', field, lookup)
}
</script>
<template>
  <div
    :class="
      inline
        ? wrap
          ? 'group/filters contents'
          : 'group/filters flex min-w-0 items-center gap-2'
        : 'flex flex-col gap-3'
    "
  >
    <p
      v-if="!inline && Object.keys(lockedFilters).length"
      class="text-xs text-muted-foreground"
    >
      {{ english ? 'Context filters are fixed by this page.' : 'Контекстные фильтры закреплены страницей.' }}
    </p>
    <ViewFilterCondition
      v-for="row in conditions"
      :key="row.key"
      :field="row.field!"
      :model-value="row.value"
      :lookup="row.lookup"
      :lookups="availableLookups(row.field!, row.key)"
      :selected-items="selectedItems(row.field!.field)"
      :inline="inline"
      :disabled="disabled"
      :size="size"
      :locale="locale"
      @update:model-value="set(row.key, $event)"
      @lookup="replace(row.key, row.field!, $event)"
      @remove="remove(row.key)"
    />
    <AppSelect
      v-if="showAdd"
      v-model:open="addOpen"
      :disabled="disabled"
      variant="outline"
      :size="size"
      :model-value="null"
      :items="
        fields.map((field) => ({
          id: field.field,
          name: field.label,
          icon: filterIcon(field),
          disabled: !availableLookups(field).length
        }))
      "
      emit-value
      :placeholder="english ? 'Add condition' : 'Добавить условие'"
      :hide-dropdown-icon="inline"
      :aria-label="english ? 'Add filter' : 'Добавить фильтр'"
      :class="
        inline && [
          'shrink-0 transition-opacity group-hover/toolbar:opacity-100 group-hover/toolbar:pointer-events-auto group-hover/filters:opacity-100 group-hover/filters:pointer-events-auto focus-within:opacity-100 focus-within:pointer-events-auto',
          !alwaysShowAdd && !addOpen && 'opacity-0 pointer-events-none'
        ]
      "
      :style="inline ? { '--add-filter-size': appControlStyles.input[size].height } : undefined"
      :locale="locale"
      class="text-muted-foreground [&_[data-app-select-trigger]]:w-[var(--add-filter-size)] [&_[data-app-select-trigger]]:!px-0 [&_[data-app-select-trigger]]:justify-center"
      @update:model-value="add"
    >
      <template
        v-if="inline"
        #trigger
      >
        <span class="flex w-full items-center justify-center"><AppIcon
          :icon="Plus"
          :size="appControlIconSize[size]"
        /></span>
      </template>
      <template #item="{ item, label }">
        <span class="flex items-center gap-2"><AppIcon
          :icon="item.icon"
          class="text-muted-foreground"
        /><span>{{ label }}</span></span>
      </template>
    </AppSelect>
  </div>
</template>
