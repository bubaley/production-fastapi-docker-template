<template>
  <main class="flex min-h-dvh items-center justify-center bg-background px-4 py-12">
    <div class="w-full max-w-sm space-y-8">
      <AppLogo class="mx-auto w-fit" />
      <AppCard padding="lg">
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
              :loading="login.isLoading.value"
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
import { isApiError } from '~/shared/api/client'

const email = ref('')
const password = ref('')
const router = useRouter()
const toast = useToast()
const { login } = useSession()
const loginHandler = async () => {
  if (login.isLoading.value) return
  try {
    await login.mutateAsync({ email: email.value, password: password.value })
  } catch (error) {
    if (isApiError(error, 401) || isApiError(error, 400)) toast.error('Неверная почта или пароль')
    else if (isApiError(error, 429)) toast.error('Слишком много попыток входа. Попробуйте позже')
    else toast.error('Не удалось войти. Попробуйте ещё раз')
    return
  }
  await router.replace(safeRedirect(router.currentRoute.value.query.redirect) ?? { name: 'home' })
}
</script>
