<template>
  <AppSection
    title="Быстрые ссылки"
    description="Разделы, с которых начинается работа"
    title-size="md"
  >
    <nav
      aria-label="Быстрые ссылки"
      class="flex flex-col"
    >
      <NuxtLink
        v-for="link in links"
        :key="link.label"
        :to="link.to"
        class="group -mx-2 flex min-w-0 items-center gap-3 rounded-md px-2 py-2.5 transition-colors outline-none hover:bg-row-hover focus-visible:ring-2 focus-visible:ring-ring"
      >
        <span class="flex size-8 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
          <AppIcon
            :icon="link.icon"
            size="md"
          />
        </span>
        <span class="min-w-0 flex-1">
          <span class="block truncate text-sm font-medium">{{ link.label }}</span>
          <span class="block truncate text-sm text-muted-foreground">{{ link.description }}</span>
        </span>
        <AppIcon
          :icon="ChevronRight"
          size="sm"
          class="shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5"
        />
      </NuxtLink>
    </nav>
  </AppSection>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { Building, ChevronRight, Palette, User, Users } from '@lucide/vue'

const props = defineProps<{ isSuperuser: boolean }>()

type HomeLink = { label: string; description: string; icon: Component; to: RouteLocationRaw }

const links = computed<HomeLink[]>(() => [
  {
    label: 'Профиль',
    description: 'Имя, пароль, сеансы и токены API',
    icon: User,
    to: { name: 'settings-profile' },
  },
  {
    label: 'Организации',
    description: 'Ваши рабочие пространства и их участники',
    icon: Building,
    to: { name: 'settings-organizations' },
  },
  ...(props.isSuperuser
    ? [
        {
          label: 'Пользователи',
          description: 'Все учётные записи сервера',
          icon: Users,
          to: { name: 'settings-users' },
        },
      ]
    : []),
  {
    label: 'Компоненты интерфейса',
    description: 'Каталог элементов, из которых собраны экраны',
    icon: Palette,
    to: { name: 'ui' },
  },
])
</script>
