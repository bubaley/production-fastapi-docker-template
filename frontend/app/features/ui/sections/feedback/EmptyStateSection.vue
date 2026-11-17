<script setup lang="ts">
import { CircleAlert, FolderPlus, Plus, RotateCw, Search, Store, Users, X } from '@lucide/vue'
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
</script>

<template>
  <UiDemo
    title="Default"
    code='variant="default" align="center" bordered'
    description="In place of a page section or a large block: dashed frame, no fill, centered. One primary action and at most one secondary."
    bare
  >
    <AppEmptyState
      :icon="Store"
      title="No stores yet"
      description="Add a store and choose whether this item is shown or hidden there."
    >
      <template #actions>
        <AppButton
          label="Add store"
          :icon="Plus"
          @click="toast.default('Store added')"
        />
        <AppButton
          label="How it works"
          variant="outline"
        />
      </template>
    </AppEmptyState>
  </UiDemo>
  <UiDemo
    title="Plain, aligned to the start"
    code=':bordered="false" align="start"'
    description="Inside a section or card that already has its own frame: no border, no padding, left-aligned with the content around it."
  >
    <AppSection
      title="Members"
      title-size="md"
    >
      <AppEmptyState
        :icon="Users"
        :bordered="false"
        align="start"
        title="No members yet"
        description="Invite colleagues so they can work with projects."
      >
        <template #actions>
          <AppButton
            label="Invite"
            :icon="Plus"
          />
        </template>
      </AppEmptyState>
    </AppSection>
  </UiDemo>
  <UiDemo
    title="Quiet, inside tables and lists"
    code='variant="quiet"'
    description="What AppTable and AppList render with no rows or on a load error: a small muted icon and regular text-sm, no title and no frame. The error keeps role=alert."
  >
    <div class="flex flex-col gap-4">
      <AppEmptyState
        variant="quiet"
        description="Здесь пока пусто"
      />
      <AppEmptyState
        variant="quiet"
        tone="destructive"
        :icon="CircleAlert"
        description="Не удалось загрузить данные"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Why it is empty"
    code='tone="primary | muted | destructive"'
    description="primary — no data yet, offer to create. muted — nothing found, offer to reset, no primary action. destructive — failed to load, only a secondary «Retry»."
    bare
  >
    <div class="grid gap-4 lg:grid-cols-3">
      <AppEmptyState
        size="sm"
        :icon="FolderPlus"
        title="No projects yet"
        description="Projects appear here once you create the first one."
      >
        <template #actions>
          <AppButton
            size="sm"
            label="Create project"
            :icon="Plus"
          />
        </template>
      </AppEmptyState>
      <AppEmptyState
        size="sm"
        :icon="Search"
        tone="muted"
        title="Nothing found"
        description="Try another query or reset the filters."
      >
        <template #actions>
          <AppButton
            size="sm"
            variant="outline"
            label="Reset filters"
            :icon="X"
          />
        </template>
      </AppEmptyState>
      <AppEmptyState
        size="sm"
        :icon="CircleAlert"
        tone="destructive"
        title="Could not load projects"
        description="The server did not respond. Your data is safe — try again."
      >
        <template #actions>
          <AppButton
            size="sm"
            variant="outline"
            label="Retry"
            :icon="RotateCw"
          />
        </template>
      </AppEmptyState>
    </div>
  </UiDemo>
  <UiDemo
    title="Inline"
    code='variant="inline" size="sm"'
    description="A row inside a card, table or form: icon, text, the action at the end. Stacks on phones."
    bare
  >
    <div class="flex flex-col gap-4">
      <AppEmptyState
        variant="inline"
        :icon="Users"
        title="No members yet"
        description="Invite colleagues so they can work with projects."
      >
        <template #actions>
          <AppButton
            variant="outline"
            label="Invite"
            :icon="Plus"
          />
        </template>
      </AppEmptyState>
      <AppEmptyState
        variant="inline"
        size="sm"
        :bordered="false"
        tone="muted"
        title="No comments"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Defaults and lists"
    code="&lt;AppEmptyState /&gt; · AppTable / AppList empty-text"
    description="Without props it shows «Здесь пока пусто» with an inbox icon. Tables and lists render it (small, muted) for empty-text and errors; pass the #empty slot for a custom state with an action."
    bare
  >
    <div class="grid gap-4 md:grid-cols-2">
      <AppEmptyState size="sm" />
      <AppTable
        :items="[]"
        empty-text="No projects yet"
      >
        <AppColumn
          field="name"
          header="Name"
        />
        <AppColumn
          field="owner"
          header="Owner"
        />
      </AppTable>
    </div>
  </UiDemo>
</template>
