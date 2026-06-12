<template>
  <AppListTemplate
    title="Токены интеграции"
    detail-mode="modal"
    template-variant="section"
    :detail-modal-props="{
      width: '32rem',
      closeOnSave: false,
      title: 'Токен интеграции',
      actionsProps: {
        hideUpdateButton: true,
      },
    }"
    :extra-params="{ user_id: props.userId }"
    :build-new-item="() => userTokenCodec.decode({ user_id: props.userId })"
    :repo="repo"
  >
    <Column
      field="value_preview"
      header="Токен"
    />
    <Column header="Последнее использование">
      <template #body="{ data }">
        <DateLabel
          v-if="data.last_used_at"
          :date="data.last_used_at"
        />
        <span
          v-else
          class="text-surface-500"
        >—</span>
      </template>
    </Column>
    <Column header="Создан">
      <template #body="{ data }">
        <DateLabel
          v-if="data.created_at"
          :date="data.created_at"
        />
      </template>
    </Column>
    <template #detail-modal="{ detailItem }">
      <div v-if="detailItem.id">
        <Message
          v-if="detailItem.value"
          severity="success"
        >
          {{ detailItem.value }}
        </Message>
        <Message v-else>{{ detailItem.value_preview }}</Message>
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
import DateLabel from '~/shared/components/labels/DateLabel.vue'

const props = defineProps<{
  userId: string
}>()

const repo = useUserTokenRepo()
</script>
