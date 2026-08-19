<template>
  <Listbox
    :model-value="null"
    :options="visibleActions"
    option-label="label"
    option-disabled="disabled"
    data-key="key"
    class="w-full border-none! bg-transparent!"
    :pt="{ option: { class: 'px-2 py-1.5 group' } }"
    @update:model-value="onSelect"
  >
    <template #option="{ option }">
      <div
        class="flex items-center gap-2.5"
        :class="option.severity === 'danger' ? 'text-red-500' : ''"
      >
        <AppIcon
          v-if="option.icon || isLoading(option)"
          class="opacity-60 transition-opacity group-hover:opacity-100 group-[.p-focus]:opacity-100"
          :icon="option.icon || ''"
          :size="14"
          :loading="isLoading(option)"
        />
        <span class="text-sm opacity-80 transition-opacity group-hover:opacity-100 group-[.p-focus]:opacity-100">
          {{ option.label }}
        </span>
      </div>
    </template>
  </Listbox>
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
