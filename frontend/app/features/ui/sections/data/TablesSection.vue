<script setup lang="ts">
import { Ellipsis } from '@lucide/vue'
import UiDemo from '../../components/UiDemo.vue'
import { useUiDemoProjects } from '../../composables/useUiDemoResource'

const { projects } = useUiDemoProjects()
const toast = useToast()
const tableState = ref('normal')
const tableVariant = ref<'default' | 'outline'>('default')
const tableVariants = [
  { label: 'default', value: 'default' },
  { label: 'outline', value: 'outline' },
]
const states = [
  { label: 'Data', value: 'normal' },
  { label: 'Loading', value: 'loading' },
  { label: 'Empty', value: 'empty' },
  { label: 'Error', value: 'error' },
]
</script>

<template>
  <UiDemo
    title="Table and declarative columns"
    code='variant="default | outline" clickable empty-text'
    description="Switch the variant and the state: the header stays through loading, empty (AppEmptyState) and error. Row actions do not open the row."
    bare
  >
    <div class="flex flex-col gap-3">
      <div class="flex flex-wrap gap-2">
        <AppSelect
          v-model="tableVariant"
          :items="tableVariants"
          item-label="label"
          item-value="value"
          emit-value
          size="sm"
          aria-label="Table variant"
        />
        <AppSelect
          v-model="tableState"
          :items="states"
          item-label="label"
          item-value="value"
          emit-value
          size="sm"
          aria-label="Table state"
        />
      </div>
      <AppTable
        empty-text="No projects yet"
        loading-text="Loading…"
        :variant="tableVariant"
        :items="tableState === 'normal' ? projects : []"
        :loading="tableState === 'loading'"
        :error="tableState === 'error' ? 'Could not load the list. Please try again.' : undefined"
        clickable
        @row-click="toast.default(`Selected project: ${$event.data.name}`)"
      >
        <AppColumn
          field="name"
          header="Name"
        />
        <AppColumn
          field="owner"
          header="Owner"
        />
        <AppColumn
          field="status"
          header="Status"
        />
        <AppColumn header="Actions">
          <template #body="{ data }">
            <AppButton
              :icon="Ellipsis"
              size="icon-sm"
              variant="ghost"
              :aria-label="`Actions: ${data.name}`"
              @click="toast.default(`Action for project «${data.name}»`)"
            />
          </template>
        </AppColumn>
      </AppTable>
    </div>
  </UiDemo>
</template>
