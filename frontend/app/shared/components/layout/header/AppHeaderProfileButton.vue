<template>
  <AppMenu
    title="Учётная запись"
    :actions="actions"
    :align="align"
    :side="side"
    content-class="min-w-56 max-w-[min(22rem,calc(100vw-2rem))]"
  >
    <!-- Who is signed in: the trigger shows only the name, so the email is here. -->
    <template #title>
      <div class="flex min-w-0 flex-col">
        <span class="truncate text-sm font-medium text-foreground">{{ displayName }}</span>
        <span
          v-if="email && email !== displayName"
          class="truncate text-xs text-muted-foreground"
          >{{ email }}</span
        >
      </div>
    </template>
    <template #trigger>
      <slot name="trigger">
        <AppButton
          variant="ghost"
          size="icon"
          :icon="User"
          aria-label="Меню профиля"
        />
      </slot>
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

withDefaults(defineProps<{ align?: 'start' | 'center' | 'end'; side?: 'top' | 'right' | 'bottom' | 'left' }>(), {
  align: 'end',
  side: 'bottom',
})

const { user, logout } = useSession()
const email = computed<string>(() => user.value?.email ?? '')
const displayName = computed<string>(() => userDisplayName(user.value) || 'Учётная запись')
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
    separatorBefore: true,
    icon: LogOut,
    action: async () => {
      try {
        await logout.mutateAsync()
      } catch {
        useToast().error('Не удалось выйти. Попробуйте ещё раз')
      }
    },
  },
]
</script>
