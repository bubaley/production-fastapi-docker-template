<template>
  <main class="flex min-h-dvh flex-col bg-background text-foreground">
    <header class="flex items-center justify-between px-4 py-4 md:px-8">
      <AppLogo />
      <AppButton
        variant="secondary"
        size="sm"
        :to="action.to"
      >
        {{ action.label }}
      </AppButton>
    </header>
    <section class="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-6 px-4 py-16">
      <h1 class="text-3xl font-semibold tracking-tight md:text-4xl">{{ name }}</h1>
      <p class="text-base text-muted-foreground md:text-lg">{{ description }}</p>
      <div>
        <AppButton
          size="lg"
          :to="action.to"
        >
          {{ action.label }}
        </AppButton>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import AppLogo from '~/shared/components/layout/header/AppLogo.vue'

const { name } = useAppConfig()
const description = 'Публичная страница шаблона. Замените этот текст описанием вашего продукта.'

// Rendered on the server with the visitor's cookie: a signed-in visitor gets the link into the app.
const { isSignedIn } = useSession()
const action = computed(() =>
  isSignedIn.value ? { label: 'Перейти в приложение', to: { name: 'home' } } : { label: 'Войти', to: { name: 'auth' } },
)

useSeoMeta({
  title: name,
  description,
  ogTitle: name,
  ogDescription: description,
  ogType: 'website',
  twitterCard: 'summary',
})
</script>
