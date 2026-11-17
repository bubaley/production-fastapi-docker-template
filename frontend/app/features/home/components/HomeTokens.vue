<template>
  <AppSection
    title="Токены API"
    description="Доступ к API для скриптов и интеграций от вашего имени"
    title-size="md"
  >
    <AppLoadingIndicator v-if="loading" />
    <AppEmptyState
      v-else-if="!tokens.length"
      title="Токенов пока нет"
      description="Создайте токен в профиле: полный ключ показывается один раз"
      :icon="KeyRound"
      size="sm"
    >
      <template #actions>
        <AppButton
          label="Создать токен"
          size="sm"
          :to="{ name: 'settings-profile' }"
        />
      </template>
    </AppEmptyState>
    <ul
      v-else
      class="flex flex-col"
    >
      <li
        v-for="token in tokens.slice(0, MAX_TOKENS)"
        :key="token.id"
        class="flex min-w-0 items-center gap-3 border-b border-border py-2.5 last:border-b-0"
      >
        <AppIcon
          :icon="KeyRound"
          size="sm"
          class="shrink-0 text-muted-foreground"
        />
        <span class="min-w-0 flex-1 truncate text-sm">{{ token.name }}</span>
        <code class="shrink-0 text-xs text-muted-foreground">{{ token.value_preview }}</code>
      </li>
      <li class="pt-3">
        <AppTextButton
          :label="tokens.length > MAX_TOKENS ? `Все токены (${tokens.length})` : 'Управлять токенами'"
          class="text-sm text-muted-foreground hover:text-foreground"
          @click="navigateTo({ name: 'settings-profile' })"
        />
      </li>
    </ul>
  </AppSection>
</template>

<script setup lang="ts">
import { KeyRound } from '@lucide/vue'
import type { UserToken } from '~/features/user/resources/userToken'

const MAX_TOKENS = 4

defineProps<{ tokens: UserToken[]; loading: boolean }>()
</script>
