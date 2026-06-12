<template>
  <div class="flex justify-center">
    <div class="col w-150">
      <AppListTemplate
        ref="organizationListRef"
        title="Выбрать организацию"
        subtitle="Выберите организацию для продолжения"
        detail-mode="modal"
        mode="list"
        :repo="useRepo('organization')"
        filter
      >
        <template #list-item="{ item }">
          <SetupCard
            :item="item"
            icon="lucide:layers"
            class="mb-4"
            @click.stop="handleItemClick(item)"
            @edit="handleItemEdit(item)"
          />
        </template>
        <template #detail-modal="{ detailItem }">
          <AppInput
            v-model="detailItem.name"
            label="Наименование"
          />
          <AppInput
            v-model="detailItem.key"
            label="Ключ"
            :disabled="!!detailItem.id"
          />
        </template>
      </AppListTemplate>
    </div>
  </div>
</template>

<script setup lang="ts">
import SetupCard from '~/features/setup/components/SetupCard.vue'

const setupStore = useSetupStore()

type SetupListRef<T extends AppModel> = {
  openItem: (item: T | null) => void
}

const organizationListRef = ref<SetupListRef<Organization> | null>(null)

const handleItemClick = (item: AppModel) => {
  setupStore.state.organization = item as Organization
  navigateTo({ name: 'home' }, { replace: true })
}

const handleItemEdit = (item: AppModel) => {
  organizationListRef.value?.openItem(item as Organization)
}

definePageMeta({
  layout: 'setup',
})
</script>
