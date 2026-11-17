<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const date = ref<string | null>('2026-09-27')
const dueAt = ref<string | null>('2026-09-27T14:30')
const range = ref({ from: '2026-09-27', to: '2026-10-02' })
</script>

<template>
  <UiDemo
    title="Date and time"
    code="AppDatePicker clearable · time"
    description="The value is an ISO string; time adds a time column."
  >
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <AppDatePicker
        v-model="date"
        label="Date"
        clearable
      />
      <AppDatePicker
        v-model="dueAt"
        label="Due date and time"
        time
        clearable
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Period"
    code='AppDateRangePicker variant="outline"'
    description="A from–to range; wrap it in AppField for a label."
  >
    <div class="max-w-sm">
      <AppField label="Date range">
        <AppDateRangePicker
          v-model="range"
          variant="outline"
        />
      </AppField>
    </div>
  </UiDemo>
  <UiDemo
    title="Date labels"
    code='AppDateLabel :date type="date | datetime"'
    description="Read-only dates in lists and cards, formatted through useDate()."
  >
    <div class="flex flex-wrap items-center gap-6 text-sm">
      <AppDateLabel
        :date="date"
        type="date"
        :is-utc="false"
        locale="en"
      />
      <AppDateLabel
        :date="dueAt"
        :is-utc="false"
        locale="en"
      />
    </div>
  </UiDemo>
</template>
