<template>
  <AppListTemplate
    title="Пользователи"
    description="Учётные записи пользователей"
    detail-route-name="settings-users-id"
    :resource="userResource"
  >
    <AppColumn
      field="email"
      header="Электронная почта"
    />
    <AppColumn
      field="first_name"
      header="Имя"
    />
    <AppColumn
      field="last_name"
      header="Фамилия"
    />
    <AppColumn header="Роль">
      <template #body="{ data }">
        <AppBadge
          v-if="data.is_superuser"
          label="Суперпользователь"
        />
        <span
          v-else
          class="text-muted-foreground"
          >Пользователь</span
        >
      </template>
    </AppColumn>
  </AppListTemplate>
</template>

<script setup lang="ts">
import { userResource } from '../resources/user'
</script>
