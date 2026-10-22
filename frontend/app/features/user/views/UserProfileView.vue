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
          <UserChangePasswordButton
            v-if="userId"
            :user-id="userId"
          />
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

const { session } = useAuth()

const data = computed(() => {
  return {
    email: session.value?.email,
    first_name: session.value?.first_name,
    last_name: session.value?.last_name,
  }
})

const userId = computed(() => (session.value?.id as string | undefined) || null)
</script>
