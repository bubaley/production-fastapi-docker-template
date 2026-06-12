<template>
  <AppListTemplate
    title="Пользователи"
    subtitle="Учётные записи"
    detail-route-name="settings-users-id"
    :repo="useRepo('user')"
  >
    <Column
      field="email"
      header="Email"
    />
    <Column
      field="first_name"
      header="Имя"
    />
    <Column
      field="last_name"
      header="Фамилия"
    />
    <Column
      field="is_superuser"
      header="Суперпользователь"
    >
      <template #body="{ data }">
        <Checkbox
          v-model="data.is_superuser"
          readonly
          binary
        />
      </template>
    </Column>
  </AppListTemplate>
</template>

<script setup lang="ts"></script>
