<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from '@lucide/vue'
import AppButton from './AppButton.vue'

const props = withDefaults(defineProps<{ min?: number; max?: number; disabled?: boolean; locale?: 'ru' | 'en' }>(), {
  min: 1,
  max: 1
})
const model = defineModel<number>({ default: 1 })
const canPrev = computed(() => model.value > props.min && !props.disabled)
const canNext = computed(() => model.value < props.max && !props.disabled)
</script>

<template>
  <div class="inline-flex items-center gap-1">
    <AppButton
      :aria-label="locale === 'en' ? 'Previous page' : 'Предыдущая страница'"
      :icon="ChevronLeft"
      size="icon-xs"
      variant="outline"
      :disabled="!canPrev"
      @click="model--"
    />
    <span class="min-w-12 text-center text-xs text-muted-foreground">{{ model }} / {{ max }}</span>
    <AppButton
      :aria-label="locale === 'en' ? 'Next page' : 'Следующая страница'"
      :icon="ChevronRight"
      size="icon-xs"
      variant="outline"
      :disabled="!canNext"
      @click="model++"
    />
  </div>
</template>
