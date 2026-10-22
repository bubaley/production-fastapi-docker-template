<script setup lang="ts">
import AppFilterToolbar from '~/shared/ui/app/filters/AppFilterToolbar.vue'
import type { ViewFilters, ViewFilterSpec } from '~/shared/ui/app/filters/types'
const name = ref('New project')
const notes = ref('Build the first workflow and verify the interface.')
const quantity = ref<number | null>(8)
const enabled = ref(true)
const checked = ref(true)
const priority = ref('normal')
const member = ref<string | null>('anna')
const members = ref<string[]>(['anna', 'mark'])
const date = ref<string | null>('2026-09-27')
const range = ref({ from: '2026-09-27', to: '2026-10-02' })
const people = [
  { id: 'anna', name: 'Anna Smith' },
  { id: 'mark', name: 'Mark Wilson' },
  { id: 'elena', name: 'Elena Parker' },
]
const filters = ref<ViewFilters>({})
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
  <div class="space-y-10">
    <AppSection
      title="Inputs and selection"
      description="Label above the control, hint or error below. All controls support keyboard navigation."
    >
      <AppCard>
        <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          <AppInput
            v-model="name"
            label="Name"
            clearable
            hint="A short, clear name"
          />
          <AppInput
            label="Search"
            placeholder="Find a project"
            is-search
            clearable
          />
          <AppInput
            label="Required field"
            error="Name is required"
            placeholder="Enter a name"
          />
          <AppSelect
            v-model="member"
            label="Owner"
            :items="people"
            item-label="name"
            item-value="id"
            emit-value
            clearable
          />
          <AppSelect
            v-model="members"
            label="Members"
            :items="people"
            item-label="name"
            item-value="id"
            emit-value
            multiple
            clearable
          />
          <AppNumberInput
            v-model="quantity"
            label="Quantity"
            :min="0"
            :max="100"
          />
          <AppDatePicker
            v-model="date"
            label="Date"
            clearable
          />
          <AppField label="Date range">
            <AppDateRangePicker
              v-model="range"
              variant="outline"
              size="default"
            />
          </AppField>
          <AppInput
            label="Disabled input"
            model-value="Read only"
            disabled
          />
          <AppTextarea
            v-model="notes"
            label="Description"
            class="md:col-span-2"
            :rows="3"
          />
          <div class="space-y-4 pt-6">
            <AppCheckbox
              v-model="checked"
              label="Receive notifications"
            />
            <label class="flex items-center gap-2 text-sm"
              ><AppSwitch
                v-model="enabled"
                aria-label="Project is active"
              />Project is active</label
            >
            <div class="flex gap-4">
              <AppRadio
                v-model="priority"
                val="normal"
                label="Normal"
              /><AppRadio
                v-model="priority"
                val="high"
                label="High"
              />
            </div>
          </div>
        </div>
      </AppCard>
    </AppSection>
    <AppSection
      title="Filters"
      description="Add a condition with +: name, status, date or activity."
    >
      <AppCard class="space-y-4">
        <AppFilterToolbar
          v-model="filters"
          v-model:search="filterSearch"
          show-search
          :spec="spec"
          always-show-add
          wrap
        />
        <p class="text-xs text-muted-foreground">
          {{
            Object.keys(filters).length ? `Active conditions: ${Object.keys(filters).length}` : 'No conditions added'
          }}
        </p>
      </AppCard>
    </AppSection>
  </div>
</template>
