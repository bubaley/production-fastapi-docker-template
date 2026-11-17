<template>
  <main class="flex min-h-dvh items-center justify-center bg-background px-4 py-12">
    <div class="w-full max-w-md space-y-8">
      <AppLogo class="mx-auto w-fit" />
      <AppCard padding="lg">
        <AppSection
          title="Первый запуск"
          description="Создайте администратора: он получит полный доступ и сможет добавить остальных пользователей"
          template-variant="flat-section"
        >
          <form
            class="space-y-4"
            @submit.prevent="submit"
          >
            <AppInput
              v-if="tokenRequired"
              v-model="form.setupToken"
              label="Ключ установки"
              hint="Значение SETUP_TOKEN из окружения сервера"
              type="password"
              autocomplete="off"
              required
            />
            <AppInput
              v-model="form.email"
              label="Электронная почта"
              type="email"
              autocomplete="username"
              placeholder="name@company.ru"
              maxlength="128"
              required
            />
            <div class="grid gap-4 sm:grid-cols-2">
              <AppInput
                v-model="form.firstName"
                label="Имя"
                autocomplete="given-name"
                maxlength="128"
                required
              />
              <AppInput
                v-model="form.lastName"
                label="Фамилия"
                autocomplete="family-name"
                maxlength="128"
                required
              />
            </div>
            <AppInput
              v-model="form.password"
              label="Пароль"
              type="password"
              autocomplete="new-password"
              hint="Не короче 8 символов"
              maxlength="128"
              required
            />
            <label class="flex items-center gap-2 pt-1 text-sm">
              <AppSwitch
                v-model="form.withOrganization"
                aria-label="Сразу создать организацию"
              />Сразу создать организацию
            </label>
            <template v-if="form.withOrganization">
              <AppInput
                v-model="form.organizationName"
                label="Наименование организации"
                autocomplete="organization"
                maxlength="128"
                required
              />
              <AppInput
                v-model="form.organizationKey"
                label="Ключ организации"
                hint="Короткий идентификатор, не меняется после создания"
                maxlength="128"
                required
              />
            </template>
            <AppButton
              :disabled="!canSubmit"
              :loading="complete.isLoading.value"
              type="submit"
              class="w-full"
            >
              Создать администратора
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
import { useFirstRunSetup } from '../composables/useFirstRunSetup'

const router = useRouter()
const toast = useToast()
const { status, complete } = useFirstRunSetup()
const tokenRequired = computed<boolean>(() => status.data.value?.token_required ?? false)

const form = ref({
  setupToken: '',
  email: '',
  firstName: '',
  lastName: '',
  password: '',
  withOrganization: false,
  organizationName: '',
  organizationKey: '',
})

const canSubmit = computed<boolean>(() => {
  const value = form.value
  const person = Boolean(value.email.trim() && value.firstName.trim() && value.lastName.trim() && value.password)
  const organization = !value.withOrganization || Boolean(value.organizationName.trim() && value.organizationKey.trim())
  return person && organization && (!tokenRequired.value || Boolean(value.setupToken))
})

const submit = async () => {
  if (!canSubmit.value || complete.isLoading.value) return
  const value = form.value
  try {
    await complete.mutateAsync({
      email: value.email.trim(),
      first_name: value.firstName.trim(),
      last_name: value.lastName.trim(),
      password: value.password,
      organization: value.withOrganization
        ? { name: value.organizationName.trim(), key: value.organizationKey.trim() }
        : null,
      setup_token: tokenRequired.value ? value.setupToken : null,
    })
  } catch (error) {
    if (isApiError(error, 409)) {
      toast.error('Первый запуск уже выполнен. Войдите в свою учётную запись')
      await router.replace({ name: 'auth' })
    } else if (isApiError(error, 403)) toast.error('Неверный ключ установки')
    else if (isApiError(error, 422)) toast.error('Проверьте почту, пароль и ключ организации')
    else if (isApiError(error, 429)) toast.error('Слишком много попыток. Попробуйте позже')
    else toast.error('Не удалось завершить настройку. Попробуйте ещё раз')
    return
  }
  toast.success('Администратор создан')
  await router.replace({ name: 'home' })
}
</script>
