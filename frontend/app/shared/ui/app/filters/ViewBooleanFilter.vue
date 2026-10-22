<script setup lang="ts">
import AppSwitch from '../AppSwitch.vue'
import AppSelect from '../AppSelect.vue'
import type { AppControlSize } from '../types/control'
import { appSelectSizeClasses, appSelectValueSizeClasses } from '../types/control'
import { useId } from 'vue'
const props = withDefaults(
  defineProps<{
    label: string
    clearable?: boolean
    disabled?: boolean
    size?: AppControlSize
    locale?: 'ru' | 'en'
  }>(),
  { clearable: true, size: 'md', locale: 'ru' },
)
const model = defineModel<boolean | null>({ default: null })
const switchId = useId()

function onControlClick(event: MouseEvent) {
  if ((event.target as Element).closest('[role="switch"]')) return
  event.preventDefault()
  if (!props.disabled) model.value = model.value !== true
}
</script>
<template>
  <label
    v-if="!clearable"
    :for="switchId"
    class="inline-flex shrink-0 cursor-pointer items-center gap-2 border border-input bg-background shadow-sm hover:bg-field-hover"
    :class="[appSelectSizeClasses[size], disabled && 'cursor-not-allowed opacity-50']"
    @click="onControlClick"
  >
    <span
      class="text-muted-foreground"
      :class="appSelectValueSizeClasses[size]"
      >{{ label }}</span
    >
    <AppSwitch
      :id="switchId"
      :model-value="model === true"
      :disabled="disabled"
      :size="size"
      variant="contrast"
      :aria-label="label"
      @update:model-value="model = $event"
    />
  </label>
  <AppSelect
    v-else
    :model-value="model === null ? null : String(model)"
    :items="[
      { id: 'true', name: locale === 'en' ? 'Yes' : 'Да' },
      { id: 'false', name: locale === 'en' ? 'No' : 'Нет' },
    ]"
    emit-value
    clearable
    :placeholder="label"
    :aria-label="label"
    :disabled="disabled"
    :size="size"
    :locale="locale"
    @update:model-value="model = $event == null ? null : $event === 'true'"
  />
</template>
