<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'
import { useUiDemoProjects } from '../../composables/useUiDemoResource'

const { resource } = useUiDemoProjects()
const pageSearch = ref('Anna')
const detail = ref(resource.toForm({ name: 'New project', owner: 'Anna Smith' }))
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
</script>

<template>
  <UiDemo
    title="List template"
    code='detail-mode="modal" template-variant="section" filter'
    description="Search, create and edit in a modal through a resource descriptor. Demo data stays on this page."
  >
    <AppListTemplate
      title="Projects"
      create-label="Create"
      search-placeholder="Search"
      empty-text="No projects yet"
      :resource="resource"
      filter
      item-label="name"
      detail-mode="modal"
      template-variant="section"
      :build-new-item="() => resource.toForm()"
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
  </UiDemo>
  <UiDemo
    title="Create in modal"
    code="create-in-modal"
    description="«Create» opens the #detail-modal form while rows keep detail-mode route (no detail route here, so rows stay put). The footer shows Cancel, then Save."
  >
    <AppListTemplate
      title="Projects"
      create-label="Create"
      search-placeholder="Search"
      empty-text="No projects yet"
      :resource="resource"
      create-in-modal
      template-variant="section"
      :infinite-scroll="false"
      :build-new-item="() => resource.toForm({ owner: 'Anna Smith' })"
      :detail-modal-props="{
        title: 'New project',
        closeLabel: 'Close',
        actionsProps: { labels: actionLabels, hideDeleteButton: true },
      }"
    >
      <AppColumn
        field="name"
        header="Name"
      /><AppColumn
        field="owner"
        header="Owner"
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
  </UiDemo>
  <UiDemo
    title="Page list"
    code='template-variant="page" #subheader v-model:search'
    description="In page mode #subheader (counters, a summary) sits between the header and the controls. v-model:search lets the parent preset or read the search text, e.g. from the URL: this one starts filtered."
    bare
  >
    <AppCard
      padding="none"
      class="h-96 overflow-hidden"
    >
      <AppListTemplate
        v-model:search="pageSearch"
        title="Projects"
        search-placeholder="Search"
        empty-text="No projects found"
        :resource="resource"
        template-variant="page"
        sticky="controls"
        hide-create-button
        :infinite-scroll="false"
      >
        <template #subheader>
          <div class="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <span>Search from the parent: «{{ pageSearch || '—' }}»</span>
            <AppButton
              size="sm"
              variant="outline"
              label="Preset «Mark»"
              @click="pageSearch = 'Mark'"
            />
            <AppButton
              size="sm"
              variant="ghost"
              label="Clear"
              @click="pageSearch = ''"
            />
          </div>
        </template>
        <AppColumn
          field="name"
          header="Name"
        /><AppColumn
          field="owner"
          header="Owner"
        />
      </AppListTemplate>
    </AppCard>
  </UiDemo>
  <UiDemo
    title="Detail template"
    code='mode="inline"'
    description="AppDetailTemplate uses the same actions and resource. Saving adds a record to the demo list."
  >
    <div class="max-w-xl">
      <AppDetailTemplate
        :resource="resource"
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
    </div>
  </UiDemo>
</template>
