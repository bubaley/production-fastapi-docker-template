<template>
  <AppListTemplate
    detail-mode="modal"
    template-variant="section"
    :build-new-item="() => organizationUserResource.toForm({ organization_id: organizationId })"
    :resource="organizationUserResource"
    :extra-params="{ organization_id: organizationId }"
    title="Участники организации"
  >
    <template #detail-modal="{ detailItem }">
      <AppSelect
        v-model="detailItem.user"
        label="Пользователь"
        :resource="userResource"
        :disabled="Boolean(detailItem.id)"
        option-label="email"
      />
    </template>
    <AppColumn
      header="Email"
      :format="(row) => row.user?.email || '—'"
    />
    <AppColumn
      header="Имя"
      :format="(row) => row.user?.first_name || '—'"
    />
    <AppColumn
      header="Фамилия"
      :format="(row) => row.user?.last_name || '—'"
    />
  </AppListTemplate>
</template>

<script setup lang="ts">
import { userResource } from '~/features/user/resources/user'
import { organizationUserResource } from '../resources/organizationUser'

// Members are added to the organization being viewed, not to the selected one (`organization_id` in the body).
defineProps<{
  organizationId: string
}>()
</script>
