<template>
  <AppListTemplate
    title="Токены интеграции"
    detail-mode="modal"
    template-variant="section"
    :detail-modal-props="{
      width: '32rem',
      closeOnSave: false,
      actionsProps: {
        disableRouterAutoResolving: true,
      },
    }"
    :extra-params="{ user_id: props.userId }"
    :build-new-item="() => userTokenCodec.decode({ user_id: props.userId })"
    :repo="repo"
  >
    <Column
      field="name"
      header="Наименование"
    />
    <Column
      field="value_preview"
      header="Токен"
    />
    <Column header="Последнее использование">
      <template #body="{ data }">
        <AppDateLabel
          v-if="data.last_used_at"
          :date="data.last_used_at"
        />
        <span
          v-else
          class="text-surface-500"
          >—</span
        >
      </template>
    </Column>
    <Column header="Создан">
      <template #body="{ data }">
        <AppDateLabel
          v-if="data.created_at"
          :date="data.created_at"
        />
      </template>
    </Column>
    <template #detail-modal="{ detailItem }">
      <AppInput
        v-model="detailItem.name"
        label="Наименование"
      />
      <div v-if="detailItem.id">
        <Message
          :severity="detailItem.value ? 'success' : undefined"
          class="w-full"
        >
          <div class="flex items-start gap-2 w-full">
            <span class="min-w-0 flex-1 break-all whitespace-normal">
              {{ detailItem.value || detailItem.value_preview }}
            </span>
            <AppButton
              v-if="detailItem.value"
              severity="success"
              class="shrink-0 ml-4"
              icon="lucide:copy"
              @click="copyToken(detailItem.value)"
            />
          </div>
        </Message>
      </div>
      <Message v-else>
        После сохранения полный токен будет показан в уведомлении. Сохраните его в надёжном месте.
      </Message>
    </template>
  </AppListTemplate>
</template>

<script setup lang="ts">
import Column from 'primevue/column'
import { userTokenCodec } from '../models/userToken'
import { useUserTokenRepo } from '../repos/userTokenRepo'

const props = defineProps<{
  userId: string
}>()

const repo = useUserTokenRepo()
const { notify } = useNotify()

const copyToken = async (value: string) => {
  try {
    await navigator.clipboard.writeText(value)
    notify({ summary: 'Скопировано' })
  } catch {
    notify({ severity: 'error', summary: 'Не удалось скопировать' })
  }
}
</script>
