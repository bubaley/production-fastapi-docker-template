<template>
  <div class="flex flex-col gap-6">
    <AppTitle
      title="Профиль"
      subtitle="Информация о пользователе"
    />
    <div class="flex items-center gap-md">
      <AppBlock
        variant="ghost"
        color="secondary"
        size="2xl"
        radius="md"
        icon="lucide:user"
      />
      <div>
        <div class="text-xl font-bold">{{ data.email }}</div>
        <div class="text-secondary mt-1">{{ data.first_name }} {{ data.last_name }}</div>
      </div>
    </div>
    <UserTokensSection
      v-if="userId"
      :user-id="userId"
    />
  </div>
</template>

<script setup lang="ts">
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
