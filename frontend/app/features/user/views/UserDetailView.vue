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
        v-if="isCreating"
        v-model="item.password"
        type="password"
        label="Пароль"
      />
      <div class="flex items-center gap-2">
        <Checkbox
          v-model="item.is_superuser"
          binary
          input-id="user-su"
        />
        <label for="user-su">Суперпользователь</label>
      </div>
      <div class="-mt-1.5">
        <UserChangePasswordButton
          v-if="item.id"
          :user-id="item.id"
        />
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
import UserChangePasswordButton from '../components/UserChangePasswordButton.vue'
import UserTokensSection from '../components/UserTokensSection.vue'
import { userCodec } from '../models/user'
</script>
