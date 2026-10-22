<template>
  <AppCard
    interactive
    class="mb-4 flex w-full p-4"
  >
    <div class="flex w-full items-center gap-4">
      <AppIcon
        :icon="icon"
        :size="30"
        tone="muted"
      />
      <div class="flex flex-col">
        <div class="text-lg font-bold">{{ item.name }}</div>
        <div class="text-sm text-muted-foreground">{{ item.key }}</div>
      </div>
      <div class="ml-auto">
        <AppButton
          variant="secondary"
          :icon="Pencil"
          aria-label="Изменить организацию"
          @click.stop="$emit('edit')"
        />
      </div>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { Pencil } from '@lucide/vue'
import type { Organization } from '~/features/organization/resources/organization'

defineEmits<{
  edit: []
}>()

defineProps<{
  item: Organization
  icon: Component
}>()
</script>
