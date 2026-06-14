<template>
  <div
    class="flex items-center gap-sm"
    :class="{ 'w-full *:flex-1': fullWidth }"
  >
    <AppButton
      v-for="(action, index) in visibleActions"
      :key="index"
      v-bind="getButtonProps(action, index)"
      :class="action.class"
      @click="executeAction(action, index)"
    />
  </div>
</template>

<script setup lang="ts">
import type { AppTemplateAction } from './types/template-types'

export type AppTemplateActionsProps = {
  actions?: AppTemplateAction[]
  size?: 'small' | 'large'
  fullWidth?: boolean
}

const props = withDefaults(defineProps<AppTemplateActionsProps>(), {
  actions: () => [],
  fullWidth: false,
})

const actionsLoading = ref<number[]>([])
const { notify } = useNotify()

const visibleActions = computed(() => props.actions.filter((action) => !action.hidden))

const getButtonProps = (action: AppTemplateAction, index: number) => {
  const mode = action.mode || 'both'
  return {
    ...action,
    label: mode === 'icon' ? undefined : action.label,
    icon: mode === 'label' ? undefined : action.icon,
    size: action.size || props.size,
    loading: action.loading || actionsLoading.value.includes(index),
    fluid: props.fullWidth || action.fluid,
  }
}

const executeAction = async (action: AppTemplateAction, index: number) => {
  if (actionsLoading.value.includes(index) || !action.action) return

  actionsLoading.value.push(index)
  try {
    await action.action()
    if (action.successNotification) {
      notify({ summary: action.successNotification })
    }
  } catch (error) {
    if (action.errorNotification) {
      notify({ severity: 'error', summary: action.errorNotification })
    }
    throw error
  } finally {
    actionsLoading.value = actionsLoading.value.filter((value) => value !== index)
  }
}
</script>
