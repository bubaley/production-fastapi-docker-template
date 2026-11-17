<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'
import { uiPeople, uiSlowPeopleSource } from '../../composables/useUiPeople'

const member = ref<string | null>('anna')
const members = ref<string[]>(['anna', 'mark', 'elena', 'olga'])
const slowMembers = ref<string[]>(['anna', 'mark', 'elena'])
</script>

<template>
  <UiDemo
    title="Single and multiple"
    code="emit-value · multiple · clearable"
    description="A multi-select trigger stays one line: two chips and «+N»."
  >
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <AppSelect
        v-model="member"
        label="Owner"
        :items="uiPeople"
        item-label="name"
        item-value="id"
        emit-value
        clearable
      />
      <AppSelect
        v-model="members"
        label="Members"
        :items="uiPeople"
        item-label="name"
        item-value="id"
        emit-value
        multiple
        clearable
      />
      <AppSelect
        v-model="member"
        label="Disabled select"
        :items="uiPeople"
        item-label="name"
        item-value="id"
        emit-value
        disabled
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Server source"
    code=":source filter :selected-items"
    description="A paginated source with search. Loaded options stay while the next page or a new query loads (1.2 s per page here)."
  >
    <div class="max-w-sm">
      <AppSelect
        v-model="slowMembers"
        label="Members (slow source)"
        :source="uiSlowPeopleSource"
        :selected-items="uiPeople.slice(0, 3)"
        item-label="name"
        item-value="id"
        emit-value
        multiple
        filter
        locale="en"
        hint="Two chips and «+N»; 1.2 s per page"
      />
    </div>
  </UiDemo>
</template>
