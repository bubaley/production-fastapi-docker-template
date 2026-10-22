<script setup lang="ts">
import { useUiDemoRepo, uiDemoCodec } from '../composables/useUiDemoRepo'
const repo = useUiDemoRepo()
const detail = ref(uiDemoCodec.decode({ name: 'New project', owner: 'Anna Smith' }))
const toast = useToast()
const actionLabels = {
  save: 'Save',
  cancel: 'Cancel',
  delete: 'Delete',
  deleteTitle: 'Delete project?',
  deleteDescription: 'This removes the demo project.',
  close: 'Close',
  saved: 'Saved',
  deleted: 'Deleted',
  saveError: 'Could not save',
  deleteError: 'Could not delete',
}
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
  <div class="space-y-10">
    <AppSection
      title="Table and declarative columns"
      description="AppTable + AppColumn. Row actions do not trigger row navigation."
    >
      <template #actions>
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
      </template>
      <AppTable
        empty-text="No data"
        loading-text="Loading…"
        :variant="tableVariant"
        :items="tableState === 'normal' ? repo.items : []"
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
              icon="lucide:ellipsis"
              size="icon-sm"
              variant="ghost"
              :aria-label="`Actions: ${data.name}`"
              @click="toast.default(`Action for project «${data.name}»`)"
            />
          </template>
        </AppColumn>
      </AppTable>
    </AppSection>
    <AppSection
      title="List template"
      description="Search, create and edit in a Modal using repo + codec. Demo data stays on this page."
    >
      <AppCard>
        <AppListTemplate
          title="Projects"
          create-label="Create"
          search-placeholder="Search"
          empty-text="No data"
          :repo="repo"
          filter
          item-label="name"
          detail-mode="modal"
          template-variant="section"
          :build-new-item="() => uiDemoCodec.decode({})"
          :detail-modal-props="{
            title: 'Project',
            closeLabel: 'Close',
            actionsProps: { disableRouterAutoResolving: true, labels: actionLabels },
          }"
        >
          <AppColumn
            field="name"
            header="Name"
          /><AppColumn
            field="owner"
            header="Owner"
          /><AppColumn
            field="status"
            header="Status"
          />
          <template #detail-modal="{ detailItem }">
            <AppInput
              v-model="detailItem.name"
              label="Name"
            /><AppInput
              v-model="detailItem.owner"
              label="Owner"
            />
          </template>
        </AppListTemplate>
      </AppCard>
    </AppSection>
    <AppSection
      title="Detail template"
      description="AppDetailTemplate uses the same actions and repository. Saving adds a record to the demo list."
    >
      <AppCard class="max-w-xl">
        <AppDetailTemplate
          :repo="repo"
          :item="detail"
          mode="inline"
          template-variant="section"
          title="New project"
          :actions-props="{ labels: actionLabels, hideDeleteButton: true, disableRouterAutoResolving: true }"
        >
          <template #default="{ item }">
            <AppInput
              v-model="item.name"
              label="Name"
            /><AppInput
              v-model="item.owner"
              label="Owner"
            />
          </template>
        </AppDetailTemplate>
      </AppCard>
    </AppSection>
  </div>
</template>
