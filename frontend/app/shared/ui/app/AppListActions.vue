<template>
  <div
    class="flex flex-col gap-1"
    role="group"
  >
    <AppButton
      v-for="option in visibleActions"
      :key="option.key"
      variant="ghost"
      :icon="option.icon"
      :loading="isLoading(option)"
      :disabled="option.disabled"
      :class="['w-full justify-start', option.severity === 'danger' && 'text-destructive']"
      @click="onSelect(option)"
    >
      {{ option.label }}
    </AppButton>
  </div>
</template>

<script setup lang="ts">
import type { AppButtonProps } from './AppButton.vue'

export interface AppListAction {
  key?: string
  icon?: string
  label: string
  loading?: boolean
  disabled?: boolean
  hidden?: boolean
  severity?: AppButtonProps['severity']
  action?: () => void | Promise<void>
}

const props = withDefaults(
  defineProps<{
    actions?: AppListAction[]
  }>(),
  {
    actions: () => [],
  },
)

const emit = defineEmits<{
  select: [action: AppListAction]
}>()

const loadingKeys = ref<string[]>([])

const actionKey = (action: AppListAction, index: number) => action.key || `${action.label}-${index}`

const visibleActions = computed(() =>
  props.actions
    .filter((action) => !action.hidden)
    .map((action, index) => {
      const key = actionKey(action, index)
      return {
        ...action,
        key,
        disabled: Boolean(action.disabled || action.loading || loadingKeys.value.includes(key)),
      }
    }),
)

const isLoading = (action: AppListAction) =>
  Boolean(action.loading || (action.key && loadingKeys.value.includes(action.key)))

const onSelect = async (action: AppListAction | null) => {
  if (!action || action.disabled || !action.action) return
  const key = action.key || action.label
  if (loadingKeys.value.includes(key)) return

  loadingKeys.value = [...loadingKeys.value, key]
  try {
    await action.action()
  } finally {
    loadingKeys.value = loadingKeys.value.filter((item) => item !== key)
    emit('select', action)
  }
}
</script>
