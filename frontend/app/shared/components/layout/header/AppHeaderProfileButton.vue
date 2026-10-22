<template>
  <AppMenu
    title="Учётная запись"
    :actions="actions"
  >
    <template #trigger>
      <AppButton
        variant="ghost"
        size="icon"
        :icon="User"
        aria-label="Меню профиля"
      />
    </template>
    <div class="border-t border-border px-2 pt-3 pb-2">
      <div class="mb-2 text-xs text-muted-foreground">Оформление</div>
      <AppThemeSwitcher />
    </div>
  </AppMenu>
</template>
<script setup lang="ts">
import { LogOut, User } from '@lucide/vue'
import type { AppMenuAction } from '~/shared/ui/app/AppMenu.vue'

const { logout } = useAuth()
const actions: AppMenuAction[] = [
  {
    label: 'Профиль',
    icon: User,
    action: async () => {
      await navigateTo({ name: 'settings-profile' })
    },
  },
  {
    label: 'Выйти',
    icon: LogOut,
    action: async () => {
      const result = await logout()
      if (result.error) {
        useToast().error('Не удалось выйти. Попробуйте ещё раз')
        return
      }
      await navigateTo({ name: 'auth' })
    },
  },
]
</script>
