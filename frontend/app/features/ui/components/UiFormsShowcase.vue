<script setup lang="ts">
import { Mail } from '@lucide/vue'
import AppFilterToolbar from '~/shared/ui/app/filters/AppFilterToolbar.vue'
import type { ViewFilters, ViewFilterSpec } from '~/shared/ui/app/filters/types'
import type { AppControlSize } from '~/shared/ui/app/types/control'
const sizes: AppControlSize[] = ['xs', 'sm', 'md', 'lg']
const name = ref('New project')
const notes = ref('Build the first workflow and verify the interface.')
const quantity = ref<number | null>(8)
const enabled = ref(true)
const checked = ref(true)
const channels = ref<string[]>(['email'])
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
      title="Control sizes"
      description="Inputs, selects and switches share the --size-control-* tokens with buttons."
    >
      <AppCard class="space-y-3">
        <div
          v-for="size in sizes"
          :key="size"
          class="grid items-center gap-3 sm:grid-cols-[3rem_1fr_1fr_auto_auto]"
        >
          <span class="text-xs text-muted-foreground">{{ size }}</span>
          <AppInput
            :size="size"
            placeholder="Input"
            aria-label="Input"
          />
          <AppSelect
            v-model="member"
            :size="size"
            :items="people"
            item-label="name"
            item-value="id"
            emit-value
            aria-label="Select"
          />
          <AppButton
            :size="size"
            label="Button"
            variant="outline"
          />
          <AppSwitch
            v-model="enabled"
            :size="size"
            aria-label="Switch"
          />
        </div>
      </AppCard>
    </AppSection>
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
            label="Invalid"
            error="Name is required"
            placeholder="Enter a name"
          />
          <AppInput
            label="Loading"
            model-value="Checking…"
            loading
          />
          <AppInput
            label="With icon"
            :icon="Mail"
            placeholder="name@company.com"
          />
          <AppInput
            label="Disabled"
            model-value="Read only"
            disabled
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
          <AppSelect
            v-model="member"
            label="Disabled select"
            :items="people"
            item-label="name"
            item-value="id"
            emit-value
            disabled
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
            />
          </AppField>
          <AppTextarea
            v-model="notes"
            label="Description"
            class="md:col-span-2"
            :rows="3"
          />
          <AppTextarea
            label="Invalid textarea"
            error="Too short"
            :rows="3"
          />
        </div>
      </AppCard>
    </AppSection>
    <AppSection
      title="Choice controls"
      description="AppCheckbox (boolean or array model), AppSwitch, AppRadioGroup."
    >
      <AppCard class="grid gap-6 sm:grid-cols-3">
        <div class="space-y-3">
          <AppCheckbox
            v-model="checked"
            label="Receive notifications"
          />
          <AppCheckbox
            v-model="channels"
            val="email"
            label="Email (array model)"
          />
          <AppCheckbox
            v-model="channels"
            val="sms"
            label="SMS (array model)"
          />
          <AppCheckbox
            :model-value="false"
            indeterminate
            label="Indeterminate"
          />
          <AppCheckbox
            :model-value="true"
            disabled
            label="Disabled"
          />
        </div>
        <div class="space-y-3">
          <label class="flex items-center gap-2 text-sm"
            ><AppSwitch
              v-model="enabled"
              aria-label="Project is active"
            />Project is active</label
          >
          <label class="flex items-center gap-2 text-sm"
            ><AppSwitch
              v-model="enabled"
              variant="contrast"
              aria-label="Contrast variant"
            />Contrast variant</label
          >
          <label class="flex items-center gap-2 text-sm text-muted-foreground"
            ><AppSwitch
              :model-value="false"
              disabled
              aria-label="Disabled"
            />Disabled</label
          >
        </div>
        <AppRadioGroup
          v-model="priority"
          aria-label="Priority"
          :items="[
            { label: 'Normal', value: 'normal' },
            { label: 'High', value: 'high' },
            { label: 'Disabled', value: 'none', disabled: true },
          ]"
        />
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
