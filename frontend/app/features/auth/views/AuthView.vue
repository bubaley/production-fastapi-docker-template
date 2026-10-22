<template>
  <main class="flex min-h-dvh items-center justify-center bg-background px-4 py-12">
    <div class="w-full max-w-sm space-y-8">
      <AppLogo class="mx-auto w-fit" />
      <AppCard
        variant="outlined"
        padding="lg"
      >
        <AppSection
          title="Войти"
          description="Используйте учётную запись вашей команды"
          template-variant="flat-section"
        >
          <form
            class="space-y-4"
            @submit.prevent="loginHandler"
          >
            <AppInput
              id="email"
              v-model="email"
              label="Электронная почта"
              type="email"
              autocomplete="username"
              placeholder="name@company.ru"
              required
            />
            <AppInput
              v-model="password"
              label="Пароль"
              type="password"
              autocomplete="current-password"
              required
            />
            <AppButton
              :disabled="!email || !password"
              :loading="authLoading"
              type="submit"
              class="w-full"
            >
              Войти
            </AppButton>
          </form>
        </AppSection>
      </AppCard>
    </div>
  </main>
</template>
<script setup lang="ts">
import AppLogo from '~/shared/components/layout/header/AppLogo.vue'
const email = ref('')
const password = ref('')
const authLoading = ref(false)
const router = useRouter()
const toast = useToast()
const { login } = useAuth()
const loginHandler = async () => {
  if (authLoading.value) return
  authLoading.value = true
  try {
    const result = await login({ email: email.value, password: password.value })
    if (result.error) {
      toast.error('Неверная почта или пароль')
      return
    }
    const redirect = router.currentRoute.value.query.redirect
    await router.replace(
      typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
        ? redirect
        : { name: 'home' },
    )
  } catch {
    toast.error('Не удалось войти. Попробуйте ещё раз')
  } finally {
    authLoading.value = false
  }
}
</script>
