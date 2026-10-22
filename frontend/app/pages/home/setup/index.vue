<template>
  <div class="flex justify-center">
    <div class="col w-150">
      <AppListTemplate
        ref="organizationListRef"
        title="Выбрать организацию"
        description="Выберите организацию для продолжения"
        detail-mode="modal"
        mode="list"
        :resource="organizationResource"
        search-param="name"
        filter
      >
        <template #list-item="{ item }">
          <SetupCard
            :item="item"
            :icon="Layers"
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
import { Layers } from '@lucide/vue'
import SetupCard from '~/features/setup/components/SetupCard.vue'
import { organizationResource, type Organization } from '~/features/organization/resources/organization'

const setupStore = useSetupStore()

const organizationListRef = ref<{ openItem: (item: Organization | null) => void } | null>(null)

const handleItemClick = (item: Organization) => {
  setupStore.state.organization = item
  void navigateTo({ name: 'home' }, { replace: true })
}

const handleItemEdit = (item: Organization) => {
  organizationListRef.value?.openItem(item)
}

definePageMeta({
  layout: 'setup',
  organization: false,
})
</script>
