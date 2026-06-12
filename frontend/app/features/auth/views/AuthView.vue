<template>
  <div class="px-6 pt-3">
    <AppLogo />
  </div>
  <div class="flex flex-col items-center justify-center min-h-screen">
    <div class="p-6 rounded-xl border border-surface-200 dark:border-surface-800 w-full max-w-md">
      <AppTitle
        centered
        title="Войти"
        class="mb-8"
      />
      <Form
        class="space-y-4"
        @submit="loginHandler"
      >
        <AppInput
          id="email"
          v-model="email"
          label="Email"
          placeholder="Введите email"
          class="w-full"
        />
        <AppInput
          v-model="password"
          label="Пароль"
          type="password"
          placeholder="Введите пароль"
          class="w-full"
        />
        <Button
          :disabled="!email || !password"
          :loading="authLoading"
          type="submit"
          label="Войти"
          class="w-full mt-4"
        />
      </Form>
    </div>
  </div>
</template>

<script lang="ts" setup>
import AppLogo from '~/shared/components/layout/header/AppLogo.vue'

const email = ref<string>('')
const password = ref<string>('')
const authLoading = ref<boolean>(false)
const router = useRouter()
const { notify } = useNotify()
const { login } = useAuth()

const loginHandler = async (): Promise<void> => {
  authLoading.value = true
  const result = await login({ email: email.value, password: password.value })
  if (result.error) {
    notify({ summary: 'Неверный данные', severity: 'error' })
    authLoading.value = false
    return
  }
  const redirectUrl = router.currentRoute.value.query.redirect as string
  await router.replace(redirectUrl || { name: 'home' })
}
</script>
