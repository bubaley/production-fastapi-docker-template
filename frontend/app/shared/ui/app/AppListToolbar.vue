<script setup lang="ts">
import { Search } from '@lucide/vue'
import AppFilterToolbar from './filters/AppFilterToolbar.vue'
import type { ViewFilters, ViewFilterSpec, ViewFixedField } from './filters/types'
withDefaults(
  defineProps<{
    filterSpec?: ViewFilterSpec
    fixedFields?: ViewFixedField[]
    availableFilters?: string[]
    showSearch?: boolean
    searchLoading?: boolean
    searchPlaceholder?: string
  }>(),
  { showSearch: false },
)
const filters = defineModel<ViewFilters>('filters', { default: () => ({}) })
const search = defineModel<string>('search', { default: '' })
</script>

<template>
  <div class="flex min-w-0 flex-col gap-4">
    <AppFilterToolbar
      v-if="filterSpec"
      v-model="filters"
      v-model:search="search"
      :spec="filterSpec"
      :fixed-fields="fixedFields"
      :available-fields="availableFilters"
      :show-search="showSearch"
      :search-loading="searchLoading"
      :search-placeholder="searchPlaceholder"
      always-show-add
      wrap
    >
      <template #actions><slot name="search-actions" /></template>
    </AppFilterToolbar>
    <div
      v-else-if="showSearch || $slots['search-actions']"
      class="flex flex-wrap items-center gap-2"
    >
      <AppInput
        v-if="showSearch"
        v-model="search"
        :icon="Search"
        class="max-w-xs flex-1"
        :loading="searchLoading"
        :placeholder="searchPlaceholder || 'Поиск'"
      />
      <slot name="search-actions" />
    </div>
    <slot name="filters" />
  </div>
</template>
