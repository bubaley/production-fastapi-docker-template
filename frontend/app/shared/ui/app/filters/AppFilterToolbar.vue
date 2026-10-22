<script setup lang="ts">
import { computed, watch } from 'vue'
import { LoaderCircle, Search } from '@lucide/vue'
import AppIcon from '../AppIcon.vue'
import AppInput from '../AppInput.vue'
import type { AppControlSize } from '../types/control'
import { appControlIconSize } from '../types/control'
import { conditionRows } from './filterConditions'
import ViewFixedFilter from './ViewFixedFilter.vue'
import { useFilterSelectedItems } from './useFilterSelectedItems'
import AppFilters from './AppFilters.vue'
import type { ViewFilters, ViewFilterSpec, ViewFixedField } from './types'
const props = withDefaults(
  defineProps<{
    spec: ViewFilterSpec
    visibleFields?: string[]
    availableFields?: string[]
    hiddenFields?: string[]
    fixedFields?: ViewFixedField[]
    wrap?: boolean
    showSearch?: boolean
    searchLoading?: boolean
    searchPlaceholder?: string
    showAdd?: boolean
    alwaysShowAdd?: boolean
    locale?: 'ru' | 'en'
    size?: AppControlSize
    disabled?: boolean
  }>(),
  { locale: 'ru', size: 'default', showAdd: true }
)
const filters = defineModel<ViewFilters>({ required: true })
const search = defineModel<string>('search', { default: '' })
const availableSpec = computed(() => ({
  fields: props.spec.fields.filter(
    (field) =>
      (!props.visibleFields || props.visibleFields.includes(field.field)) && !props.hiddenFields?.includes(field.field)
  )
}))
const dynamicSpec = computed(() => ({
  fields: availableSpec.value.fields.filter((field) => !props.availableFields || props.availableFields.includes(field.field))
}))
const fixed = computed(() =>
  (props.fixedFields ?? []).flatMap((config, index, all) => {
    const field = availableSpec.value.fields.find((field) => field.field === config.field)
    return field && all.findIndex((item) => item.field === config.field) === index ? [{ config, field }] : []
  })
)
const excludedKeys = computed(() =>
  fixed.value.flatMap(({ field, config }) => {
    if (config.filterKeys) return config.filterKeys
    if (config.mode === 'optional') {
      const row = conditionRows([field], filters.value)[0]
      return row?.lookup === 'range' ? [`${field.field}__gte`, `${field.field}__lte`] : row ? [row.key] : []
    }
    return config.mode === 'multiple' ? [`${field.field}__in`] : [field.field, `${field.field}__exact`]
  })
)
const initializedDefaults = new Set<string>()
watch(
  [fixed, () => props.disabled],
  () => {
    if (props.disabled) return
    const next = { ...filters.value }
    let changed = false
    for (const { field, config } of fixed.value) {
      if (initializedDefaults.has(field.field)) continue
      initializedDefaults.add(field.field)
      if (
        config.defaultValue === undefined ||
        Object.keys(next).some((key) => key.split('__')[0] === field.field || config.filterKeys?.includes(key))
      )
        continue
      const lookup =
        config.mode === 'multiple' ? 'in' : field.lookups.includes('exact') ? 'exact' : field.lookups[0] || 'exact'
      next[lookup === 'exact' ? field.field : `${field.field}__${lookup}`] = config.defaultValue
      changed = true
    }
    if (changed) filters.value = next
  },
  { immediate: true }
)
const selectedItems = useFilterSelectedItems(availableSpec, filters)
</script>
<template>
  <div
    class="group/toolbar flex w-full min-w-0 flex-wrap items-center gap-2"
    :aria-label="locale === 'en' ? 'View filters' : 'Фильтры представления'"
  >
    <div
      :class="wrap ? 'contents' : 'flex max-w-full shrink-0 self-start flex-wrap items-center gap-1.5 py-1'"
      data-filter-fixed
    >
      <AppInput
        v-if="showSearch"
        v-model="search"
        type="search"
        :icon="searchLoading ? LoaderCircle : Search"
        :aria-busy="searchLoading"
        clearable
        :size="size"
        :disabled="disabled"
        :placeholder="searchPlaceholder || (locale === 'en' ? 'Search...' : 'Поиск...')"
        :aria-label="locale === 'en' ? 'Search' : 'Поиск'"
        class="w-48 shrink-0"
      >
        <template #prepend>
          <AppIcon
            :icon="searchLoading ? LoaderCircle : Search"
            :size="appControlIconSize[size]"
            :class="searchLoading && 'animate-spin motion-reduce:animate-none'"
          />
        </template>
      </AppInput>
      <slot name="primary" />
      <template
        v-for="{ field, config } in fixed"
        :key="field.field"
      >
        <slot
          :name="`fixed-${field.field}`"
          :field="field"
          :config="config"
          :selected-items="selectedItems(field.field)"
        >
          <ViewFixedFilter
            v-model="filters"
            :field="field"
            :config="config"
            :selected-items="selectedItems(field.field)"
            :locale="locale"
            :size="size"
            :disabled="disabled"
          />
        </slot>
      </template>
    </div>
    <div
      :class="
        wrap
          ? 'contents'
          : 'flex min-w-0 flex-1 items-center gap-1.5 py-1 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden'
      "
      data-filter-dynamic
    >
      <AppFilters
        v-model="filters"
        :spec="dynamicSpec"
        :excluded-keys="excludedKeys"
        :wrap="wrap"
        :show-add="showAdd"
        :always-show-add="alwaysShowAdd"
        include-quick
        :disabled="disabled"
        inline
        :size="size"
        :locale="locale"
      />
    </div>
    <div class="ml-auto flex max-w-full shrink-0 items-center gap-1.5 overflow-x-auto py-1">
      <slot name="quick" />
      <slot name="actions" />
    </div>
  </div>
</template>
