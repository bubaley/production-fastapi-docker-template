<template>
  <AppListTemplate
    title="Токены API"
    description="Для скриптов и интеграций. Полный токен показывается один раз, при создании"
    detail-mode="modal"
    template-variant="section"
    title-size="md"
    empty-text="Токенов пока нет"
    :detail-modal-props="{
      title: 'Токен API',
      width: '32rem',
      closeOnSave: false,
      actionsProps: {
        disableRouterAutoResolving: true,
      },
    }"
    :extra-params="{ user_id: props.userId }"
    :build-new-item="() => userTokenResource.toForm({ user_id: props.userId })"
    :resource="userTokenResource"
    @save="onSave"
  >
    <AppColumn
      field="name"
      header="Название"
    />
    <AppColumn
      field="value_preview"
      header="Токен"
    />
    <AppColumn header="Последнее использование">
      <template #body="{ data }">
        <AppDateLabel
          v-if="data.last_used_at"
          :date="data.last_used_at"
        />
        <span
          v-else
          class="text-muted-foreground"
          >—</span
        >
      </template>
    </AppColumn>
    <AppColumn header="Создан">
      <template #body="{ data }">
        <AppDateLabel
          v-if="data.created_at"
          :date="data.created_at"
        />
      </template>
    </AppColumn>
    <template #detail-modal="{ detailItem }">
      <AppInput
        v-model="detailItem.name"
        label="Название"
      />
      <div v-if="detailItem.id">
        <AppCard
          :tone="detailItem.value ? 'success' : 'neutral'"
          class="w-full"
        >
          <div class="flex w-full items-start gap-2">
            <span class="min-w-0 flex-1 font-mono text-sm break-all whitespace-normal">
              {{ detailItem.value || detailItem.value_preview }}
            </span>
            <AppButton
              v-if="detailItem.value"
              variant="ghost"
              class="ml-4 shrink-0 text-success"
              :icon="Copy"
              aria-label="Скопировать токен"
              @click="copyToken(detailItem.value)"
            />
          </div>
        </AppCard>
      </div>
      <AppAlert
        v-else
        tone="neutral"
        description="Полный токен будет показан один раз, сразу после сохранения. Скопируйте его и храните в надёжном месте."
      />
    </template>
  </AppListTemplate>
</template>

<script setup lang="ts">
import { Copy } from '@lucide/vue'
import { userTokenResource, type UserToken, type UserTokenForm } from '../resources/userToken'

const props = defineProps<{
  userId: string
}>()

const toast = useToast()

// The full secret is in the create response only; the modal stays open to show it, the toast keeps a copy.
const onSave = (event: AppDetailActionsSaveResult<UserTokenForm, UserToken>) => {
  if (event.created && event.saved?.value) {
    toast.default('Токен создан', { description: event.saved.value, duration: 120_000 })
  }
}

const copyToken = async (value: string) => {
  try {
    await navigator.clipboard.writeText(value)
    toast.default('Скопировано')
  } catch {
    toast.error('Не удалось скопировать')
  }
}
</script>
