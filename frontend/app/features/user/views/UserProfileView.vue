<template>
  <AppPageView
    title="Профиль"
    description="Информация о пользователе"
  >
    <div class="flex flex-col gap-6 pt-3">
      <div class="flex flex-wrap items-center gap-4">
        <AppAvatar
          :name="data.email"
          size="xlarge"
        />
        <div>
          <div class="text-xl font-bold break-all">{{ data.email }}</div>
          <div class="mt-1 text-muted-foreground">{{ data.first_name }} {{ data.last_name }}</div>
          <div class="flex flex-wrap items-center gap-x-4">
            <UserChangePasswordButton
              v-if="userId"
              :user-id="userId"
            />
            <AppTextButton
              v-if="userId"
              label="Выйти на всех устройствах"
              tone="muted"
              class="text-sm"
              @click="logoutAllState.execute"
            />
          </div>
        </div>
      </div>
      <UserTokensSection
        v-if="userId"
        :user-id="userId"
      />
    </div>
  </AppPageView>
</template>

<script setup lang="ts">
import UserChangePasswordButton from '~/features/user/components/UserChangePasswordButton.vue'
import UserTokensSection from '~/features/user/components/UserTokensSection.vue'

const { user, logoutAll } = useSession()

const data = computed(() => ({
  email: user.value?.email,
  first_name: user.value?.first_name,
  last_name: user.value?.last_name,
}))

const userId = computed(() => user.value?.id ?? null)

// Ends every session of the user (all devices), then signs out here too.
const logoutAllState = useActionState(() => logoutAll.mutateAsync(), {
  errorNotification: 'Не удалось завершить сеансы. Попробуйте ещё раз',
})
</script>
