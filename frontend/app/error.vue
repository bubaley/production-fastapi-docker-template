<template>
  <main class="flex min-h-dvh items-center justify-center bg-background px-4 py-12">
    <div class="w-full max-w-sm space-y-8">
      <AppLogo class="mx-auto w-fit" />
      <AppCard padding="lg">
        <AppResultState
          as="h1"
          :icon="notFound ? FileQuestion : TriangleAlert"
          :tone="notFound ? 'muted' : 'warning'"
          :title="notFound ? 'Страница не найдена' : 'Что-то пошло не так'"
          :description="
            notFound
              ? 'Возможно, ссылка устарела или в адресе опечатка.'
              : 'Не удалось открыть страницу. Попробуйте обновить её через минуту.'
          "
        >
          <template #actions>
            <AppButton
              label="На главную"
              fluid
              @click="goHome"
            />
            <AppButton
              v-if="!notFound"
              variant="secondary"
              label="Обновить страницу"
              fluid
              @click="reload"
            />
          </template>
        </AppResultState>
      </AppCard>
      <p
        v-if="!notFound && error?.statusCode"
        class="text-center text-xs text-muted-foreground"
      >
        Код ошибки: {{ error.statusCode }}
      </p>
    </div>
  </main>
</template>

<script setup lang="ts">
import { FileQuestion, TriangleAlert } from '@lucide/vue'
import type { NuxtError } from '#app'
import AppLogo from '~/shared/components/layout/header/AppLogo.vue'

const props = defineProps<{ error: NuxtError | null }>()
const notFound = computed(() => props.error?.statusCode === 404)

const goHome = () => clearError({ redirect: '/' })
const reload = () => {
  if (import.meta.client) window.location.reload()
}

const { name } = useAppConfig()
useHead({ title: () => `${notFound.value ? 'Страница не найдена' : 'Ошибка'} · ${name}` })
useSeoMeta({ robots: 'noindex' })
</script>
