<template>
  <AppBlock
    variant="outlined"
    class="mb-4 flex w-full p-4"
    radius="md"
  >
    <div class="flex items-center gap-4 w-full">
      <Icon
        :name="icon"
        size="30"
        class="fg-tertiary"
      />
      <div class="flex flex-col">
        <div class="text-lg font-bold">{{ item.name }}</div>
        <div class="fg-secondary text-sm">{{ item.key }}</div>
      </div>
      <div class="ml-auto">
        <AppButton
          severity="secondary"
          icon="lucide:pencil"
          @click.stop="$emit('edit')"
        />
      </div>
    </div>
  </AppBlock>
</template>

<script setup lang="ts">
import type { Organization } from '~/features/organization/models/organization'

defineEmits<{
  edit: []
}>()

defineProps<{
  item: Organization
  icon: string
}>()
</script>
