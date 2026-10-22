<template>
  <AppMenu
    title="Учётная запись"
    :actions="actions"
  >
    <template #trigger>
      <AppButton
        variant="ghost"
        size="icon"
        icon="lucide:user"
        aria-label="Меню профиля"
      />
    </template>
  </AppMenu>
</template>
<script setup lang="ts">
const colorMode = useColorMode()
const { logout } = useAuth()
const actions = computed(() => [
  { label: 'Профиль', icon: 'lucide:user', action: async () => { await navigateTo({ name: 'settings-profile' }) } },
  { label: colorMode.value === 'dark' ? 'Светлая тема' : 'Тёмная тема', icon: colorMode.value === 'dark' ? 'lucide:sun' : 'lucide:moon', action: () => { colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark' } },
  { label: 'Выйти', icon: 'lucide:log-out', separatorBefore: true, action: async () => {
    const result = await logout()
    if (result.error) { useToast().error('Не удалось выйти. Попробуйте ещё раз'); return }
    await navigateTo({ name: 'auth' })
  } },
])
</script>
