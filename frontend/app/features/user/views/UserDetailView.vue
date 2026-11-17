<template>
  <AppDetailTemplate
    title="Пользователь"
    :resource="userResource"
  >
    <template #default="{ item, isCreating }">
      <AppInput
        v-model="item.email"
        label="Электронная почта"
        type="email"
      />
      <AppInput
        v-model="item.first_name"
        label="Имя"
      />
      <AppInput
        v-model="item.last_name"
        label="Фамилия"
      />
      <AppInput
        v-if="isCreating"
        v-model="item.password"
        type="password"
        label="Пароль"
      />
      <AppCheckbox
        v-model="item.is_superuser"
        label="Суперпользователь"
      />
      <div v-if="item.id">
        <UserChangePasswordButton :user-id="item.id" />
      </div>
      <UserTokensSection
        v-if="item.id"
        :user-id="item.id"
      />
    </template>
  </AppDetailTemplate>
</template>

<script setup lang="ts">
import UserChangePasswordButton from '../components/UserChangePasswordButton.vue'
import UserTokensSection from '../components/UserTokensSection.vue'
import { userResource } from '../resources/user'
</script>
