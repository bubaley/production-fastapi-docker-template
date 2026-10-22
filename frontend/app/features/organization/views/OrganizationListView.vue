<template>
  <AppListTemplate
    title="Организации"
    detail-route-name="settings-organizations-id"
    :resource="organizationResource"
    search-param="name"
    :filter-spec="filterSpec"
    :fixed-fields="[{ field: 'key', mode: 'single' }]"
    :available-filters="['key']"
    description="Управление организациями"
  >
    <AppColumn
      field="name"
      header="Наименование"
    />
    <AppColumn
      field="key"
      header="Ключ"
    />
  </AppListTemplate>
</template>

<script setup lang="ts">
import type { ViewFilterSpec } from '~/shared/ui/app/filters/types'
import { organizationResource } from '../resources/organization'

const filterSpec: ViewFilterSpec = {
  fields: [{ field: 'key', label: 'Ключ', kind: 'text', lookups: ['icontains', 'exact'] }],
}
</script>
