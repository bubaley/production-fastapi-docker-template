<template>
  <AppTextButton
    v-if="userId"
    label="Сменить пароль"
    severity="secondary"
    class="text-sm"
    @click="open"
  />
  <AppConfirmModal
    v-model="visible"
    title="Смена пароля"
    hide-subtitle
    confirm-text="Сохранить"
    :confirm="submitState.execute"
  >
    <div class="flex flex-col gap-3">
      <AppInput
        v-if="requireCurrentPassword"
        v-model="currentPassword"
        type="password"
        label="Текущий пароль"
      />
      <AppInput
        v-model="newPassword"
        autocomplete="new-password"
        type="password"
        label="Новый пароль"
      />
      <AppInput
        v-model="newPasswordRepeat"
        autocomplete="new-password"
        type="password"
        label="Повторите пароль"
      />
    </div>
  </AppConfirmModal>
</template>

<script setup lang="ts">
const props = defineProps<{
  userId: string
}>()

const { session } = useAuth()
const { notify } = useNotify()
const repo = useRepo('user')

const visible = ref(false)
const currentPassword = ref('')
const newPassword = ref('')
const newPasswordRepeat = ref('')

const requireCurrentPassword = computed(() => !session.value?.is_superuser)

const resetForm = () => {
  currentPassword.value = ''
  newPassword.value = ''
  newPasswordRepeat.value = ''
}

const open = () => {
  resetForm()
  visible.value = true
}

const submitState = useActionState(
  async () => {
    if (!newPassword.value) {
      notify({ severity: 'error', summary: 'Укажите новый пароль' })
      throw new Error('empty')
    }
    if (newPassword.value !== newPasswordRepeat.value) {
      notify({ severity: 'error', summary: 'Пароли не совпадают' })
      throw new Error('mismatch')
    }
    if (requireCurrentPassword.value && !currentPassword.value) {
      notify({ severity: 'error', summary: 'Укажите текущий пароль' })
      throw new Error('current')
    }
    try {
      await repo.changePassword(props.userId, {
        ...(requireCurrentPassword.value ? { current_password: currentPassword.value } : {}),
        new_password: newPassword.value,
      })
    } catch (error) {
      notify({ severity: 'error', summary: 'Не удалось сменить пароль' })
      throw error
    }
  },
  {
    successNotification: 'Пароль изменён',
  },
)
</script>
