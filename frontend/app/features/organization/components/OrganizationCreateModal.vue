<template>
  <AppModal
    v-model="open"
    title="Новая организация"
    :description="
      required
        ? 'Чтобы начать работу, создайте организацию. Позже в неё можно пригласить коллег'
        : 'Вы станете её участником, и она откроется сразу после создания'
    "
    width="28rem"
    :closeable="!required"
    :prevent-outside-close="required"
    :escape-disabled="required"
  >
    <form
      :id="formId"
      class="flex flex-col gap-3"
      @submit.prevent="createState.execute"
    >
      <AppInput
        v-model="form.name"
        label="Наименование"
        autocomplete="organization"
        maxlength="128"
      />
      <AppInput
        v-model="form.key"
        label="Ключ"
        hint="Короткий идентификатор латиницей, не меняется после создания"
        maxlength="128"
      />
    </form>
    <template #footer>
      <!-- Without an organization the app has nothing to show: signing out is the only other way out. -->
      <AppButton
        v-if="required"
        variant="ghost"
        label="Выйти"
        :loading="logoutState.loading.value"
        @click="logoutState.execute"
      />
      <AppButton
        v-else
        variant="secondary"
        label="Отменить"
        @click="open = false"
      />
      <AppButton
        type="submit"
        :form="formId"
        label="Создать"
        :disabled="!canSubmit"
        :loading="createState.loading.value"
      />
    </template>
  </AppModal>
</template>

<script setup lang="ts">
import { useResourceMutations } from '~/shared/api/useResource'
import { organizationResource, type OrganizationForm } from '../resources/organization'

defineProps<{
  /** The user has no organization: the modal cannot be dismissed, only completed or left by signing out. */
  required?: boolean
}>()

const open = defineModel<boolean>({ default: false })

const formId = useId()
const setupStore = useSetupStore()
const { logout } = useSession()
const { save } = useResourceMutations(organizationResource)

const form = ref<OrganizationForm>(organizationResource.toForm())
watch(open, (value) => {
  if (value) form.value = organizationResource.toForm()
})
const canSubmit = computed<boolean>(() => Boolean(form.value.name.trim() && form.value.key.trim()))

const createState = useActionState(
  async () => {
    if (!canSubmit.value) return
    const { item } = await save.mutateAsync({ ...form.value, name: form.value.name.trim(), key: form.value.key.trim() })
    setupStore.state.organization = { id: item.id, name: item.name, key: item.key }
    open.value = false
    await navigateTo({ name: 'home' })
  },
  { successNotification: 'Организация создана', errorNotification: 'Не удалось создать организацию' },
)

const logoutState = useActionState(() => logout.mutateAsync(), {
  errorNotification: 'Не удалось выйти. Попробуйте ещё раз',
})
</script>
