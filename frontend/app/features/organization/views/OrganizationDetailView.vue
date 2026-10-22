<template>
  <AppDetailTemplate
    title="Организация"
    :resource="organizationResource"
    :back-action="() => navigateTo({ name: 'settings-organizations' })"
  >
    <template #default="{ item }">
      <AppInput
        v-model="item.name"
        label="Наименование"
      />
      <AppInput
        v-model="item.key"
        label="Ключ"
        :disabled="Boolean(item.id)"
      />
      <OrganizationMembersList
        v-if="item.id"
        :organization-id="item.id"
        class="mt-6 mb-0!"
      />
    </template>
  </AppDetailTemplate>
</template>

<script setup lang="ts">
import OrganizationMembersList from './OrganizationMembersList.vue'
import { organizationResource } from '../resources/organization'
</script>
