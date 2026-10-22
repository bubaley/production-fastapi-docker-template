<template>
  <AppListTemplate
    title="Пользователи"
    description="Учетные записи пользователей"
    detail-route-name="settings-users-id"
    :resource="userResource"
  >
    <AppColumn
      field="email"
      header="Email"
    />
    <AppColumn
      field="first_name"
      header="Имя"
    />
    <AppColumn
      field="last_name"
      header="Фамилия"
    />
    <AppColumn
      field="is_superuser"
      header="Суперпользователь"
    >
      <template #body="{ data }">
        <AppCheckbox
          v-model="data.is_superuser"
          readonly
          binary
        />
      </template>
    </AppColumn>
  </AppListTemplate>
</template>

<script setup lang="ts">
import { userResource } from '../resources/user'
</script>
