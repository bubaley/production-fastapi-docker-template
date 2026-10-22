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
    <AppColumn
      field="name"
      header="Наименование"
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
        label="Наименование"
      />
      <div v-if="detailItem.id">
        <AppCard
          :tone="detailItem.value ? 'success' : 'neutral'"
          class="w-full"
        >
          <div class="flex w-full items-start gap-2">
            <span class="min-w-0 flex-1 break-all whitespace-normal">
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
      <AppCard v-else>
        После сохранения полный токен будет показан в уведомлении. Сохраните его в надёжном месте.
      </AppCard>
    </template>
  </AppListTemplate>
</template>

<script setup lang="ts">
import { Copy } from '@lucide/vue'
import { userTokenCodec } from '../models/userToken'
import { useUserTokenRepo } from '../repos/userTokenRepo'

const props = defineProps<{
  userId: string
}>()

const repo = useUserTokenRepo()
const toast = useToast()

const copyToken = async (value: string) => {
  try {
    await navigator.clipboard.writeText(value)
    toast.default('Скопировано')
  } catch {
    toast.error('Не удалось скопировать')
  }
}
</script>
