<template>
  <AppListTemplate
    detail-mode="modal"
    template-variant="section"
    :build-new-item="() => organizationUserCodec.decode({ organization_id: organization.id, user_id: null })"
    :repo="useRepo('organizationUser')"
    :extra-params="{ organization_id: organization.id }"
    title="Участники организации"
  >
    <template #detail-modal="{ detailItem }">
      <CSelect
        v-model="detailItem.user"
        label="Пользователь"
        :repo="useRepo('user')"
        option-label="email"
      />
    </template>
    <CColumn
      header="Email"
      :format="(row) => row.user?.email || '—'"
    />
    <CColumn
      header="Имя"
      :format="(row) => row.user?.first_name || '—'"
    />
    <CColumn
      header="Фамилия"
      :format="(row) => row.user?.last_name || '—'"
    />
  </AppListTemplate>
</template>

<script setup lang="ts">
defineProps<{
  organization: Organization
}>()
</script>
