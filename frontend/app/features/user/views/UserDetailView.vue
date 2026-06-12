<template>
  <AppDetailTemplate
    :build-new-item="() => userCodec.decode({ is_superuser: false })"
    title="Пользователь"
    :repo="useRepo('user')"
  >
    <template #default="{ item, isCreating }">
      <AppInput
        v-model="item.email"
        label="Email"
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
        v-model="item.password"
        type="password"
        :label="isCreating ? 'Пароль' : 'Новый пароль (оставьте пустым, чтобы не менять)'"
      />
      <div class="flex items-center gap-2">
        <Checkbox
          v-model="item.is_superuser"
          binary
          input-id="user-su"
        />
        <label for="user-su">Суперпользователь</label>
      </div>
      <UserTokensSection
        v-if="item.id"
        :user-id="item.id"
      />
    </template>
  </AppDetailTemplate>
</template>

<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import UserTokensSection from '../components/UserTokensSection.vue'
import { userCodec } from '../models/user'
</script>
