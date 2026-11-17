<template>
  <AppPageView
    title="Профиль"
    description="Ваши данные, вход и токены для интеграций"
    max-width="md"
    align="start"
  >
    <!-- Settings rows read label ↔ control: the `md` page column keeps both in one glance. -->
    <div class="flex min-w-0 flex-col gap-10 pt-2">
      <div class="flex min-w-0 items-center gap-4">
        <AppAvatar
          :name="displayName"
          size="large"
          variant="soft"
        />
        <div class="min-w-0">
          <div class="truncate text-lg font-semibold">{{ displayName }}</div>
          <div
            v-if="user?.email && displayName !== user.email"
            class="truncate text-sm text-muted-foreground"
          >
            {{ user.email }}
          </div>
        </div>
      </div>

      <AppSection
        title="Учётная запись"
        title-size="md"
        class="gap-1"
      >
        <form
          class="min-w-0"
          @submit.prevent="saveState.execute"
        >
          <AppSettingRow
            label="Имя"
            for-id="profile-first-name"
          >
            <AppInput
              id="profile-first-name"
              v-model="firstName"
              class="w-full sm:w-64"
              autocomplete="given-name"
              maxlength="128"
            />
          </AppSettingRow>
          <AppSettingRow
            label="Фамилия"
            for-id="profile-last-name"
          >
            <AppInput
              id="profile-last-name"
              v-model="lastName"
              class="w-full sm:w-64"
              autocomplete="family-name"
              maxlength="128"
            />
          </AppSettingRow>
          <AppSettingRow
            label="Электронная почта"
            description="Для входа. Изменить её может администратор сервера"
          >
            <span class="min-w-0 text-sm break-all">{{ user?.email }}</span>
          </AppSettingRow>
          <div
            v-if="dirty"
            class="flex justify-end gap-2 pt-3"
          >
            <AppButton
              variant="secondary"
              label="Отменить"
              @click="reset"
            />
            <AppButton
              type="submit"
              label="Сохранить"
              :loading="saveState.loading.value"
            />
          </div>
        </form>
      </AppSection>

      <AppSection
        v-if="userId"
        title="Безопасность"
        title-size="md"
        class="gap-1"
      >
        <div>
          <AppSettingRow
            label="Пароль"
            description="Другие браузеры выйдут из аккаунта, токены API продолжат работать"
          >
            <UserChangePasswordButton :user-id="userId" />
          </AppSettingRow>
          <AppSettingRow
            label="Сеансы"
            description="Выйти здесь или завершить вход во всех браузерах и приложениях"
          >
            <AppButton
              variant="outline"
              label="Выйти"
              :loading="logoutState.loading.value"
              @click="logoutState.execute"
            />
            <AppButton
              variant="outline"
              label="Выйти на всех устройствах"
              :loading="logoutAllState.loading.value"
              @click="logoutAllState.execute"
            />
          </AppSettingRow>
        </div>
      </AppSection>

      <UserTokensSection
        v-if="userId"
        :user-id="userId"
      />
    </div>
  </AppPageView>
</template>

<script setup lang="ts">
import { useQueryCache } from '@pinia/colada'
import UserChangePasswordButton from '~/features/user/components/UserChangePasswordButton.vue'
import UserTokensSection from '~/features/user/components/UserTokensSection.vue'
import { usersPartialUpdate } from '~/shared/api/generated'
import { useApiClient } from '~/shared/api/useResource'
import { SESSION_KEY } from '~/shared/composables/useSession'

const { user, logout, logoutAll } = useSession()
const client = useApiClient()
const queryCache = useQueryCache()

const userId = computed<string | null>(() => user.value?.id ?? null)
const displayName = computed<string>(() => userDisplayName(user.value) || 'Профиль')

const firstName = ref<string>('')
const lastName = ref<string>('')
const reset = (): void => {
  firstName.value = user.value?.first_name ?? ''
  lastName.value = user.value?.last_name ?? ''
}
watch(() => [user.value?.first_name, user.value?.last_name], reset, { immediate: true })
const dirty = computed<boolean>(
  () =>
    firstName.value.trim() !== (user.value?.first_name ?? '') ||
    lastName.value.trim() !== (user.value?.last_name ?? ''),
)

const saveState = useActionState(
  async () => {
    if (!userId.value) return
    await usersPartialUpdate({
      client,
      throwOnError: true,
      path: { item_id: userId.value },
      body: { first_name: firstName.value.trim(), last_name: lastName.value.trim() },
    })
    // The sidebar, the account menu and this page read the name from the session.
    await queryCache.invalidateQueries({ key: [...SESSION_KEY] })
  },
  { successNotification: 'Сохранено', errorNotification: 'Не удалось сохранить' },
)

const logoutState = useActionState(() => logout.mutateAsync(), {
  errorNotification: 'Не удалось выйти. Попробуйте ещё раз',
})

// Ends every session of the user (all devices), then signs out here too.
const logoutAllState = useActionState(() => logoutAll.mutateAsync(), {
  errorNotification: 'Не удалось завершить сеансы. Попробуйте ещё раз',
})
</script>
