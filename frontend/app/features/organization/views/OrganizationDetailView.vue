<template>
  <AppDetailTemplate
    :build-new-item="() => organizationCodec.decode({})"
    title="Организация"
    :repo="useRepo('organization')"
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
      />
      <OrganizationMembersList
        v-if="item.id"
        :organization="item"
        class="mb-0! mt-6"
      />
    </template>
  </AppDetailTemplate>
</template>

<script setup lang="ts">
import OrganizationMembersList from './OrganizationMembersList.vue'
import { organizationCodec } from '../models/organization'
</script>
