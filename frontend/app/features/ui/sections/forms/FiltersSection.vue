<script setup lang="ts">
import AppFilterToolbar from '~/shared/ui/app/filters/AppFilterToolbar.vue'
import type { ViewFilters, ViewFilterSpec } from '~/shared/ui/app/filters/types'
import UiDemo from '../../components/UiDemo.vue'

const filters = ref<ViewFilters>({})
const narrowFilters = ref<ViewFilters>({})
const filterSearch = ref('')
const spec: ViewFilterSpec = {
  fields: [
    { field: 'name', label: 'Name', kind: 'text', lookups: ['icontains', 'exact'] },
    {
      field: 'status',
      label: 'Status',
      kind: 'choice',
      lookups: ['in', 'exact'],
      items: [
        { id: 'active', name: 'In progress' },
        { id: 'done', name: 'Success' },
      ],
    },
    { field: 'created_at', label: 'Created at', kind: 'date', lookups: ['gte', 'lte', 'exact'] },
    { field: 'enabled', label: 'Active', kind: 'boolean', lookups: ['exact'] },
  ],
}
</script>

<template>
  <UiDemo
    title="Search and conditions"
    code=":spec show-search always-show-add wrap"
    description="Add a condition with +: name, status, date or activity."
  >
    <div class="flex flex-col gap-4">
      <AppFilterToolbar
        v-model="filters"
        v-model:search="filterSearch"
        show-search
        :spec="spec"
        always-show-add
        wrap
        locale="en"
      />
      <p class="text-xs text-muted-foreground">
        {{ Object.keys(filters).length ? `Active conditions: ${Object.keys(filters).length}` : 'No conditions added' }}
      </p>
    </div>
  </UiDemo>
  <UiDemo
    title="Fixed fields in a narrow container"
    code=':fixed-fields="[{ field, mode }]"'
    description="Without wrap the row scrolls horizontally; shadows are not clipped."
  >
    <div class="max-w-xs">
      <AppFilterToolbar
        v-model="narrowFilters"
        :spec="spec"
        :fixed-fields="[
          { field: 'status', mode: 'multiple' },
          { field: 'enabled', mode: 'optional' },
        ]"
        always-show-add
        locale="en"
      />
    </div>
  </UiDemo>
</template>
