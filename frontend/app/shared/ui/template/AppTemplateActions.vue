<template>
  <div
    class="flex items-center gap-2"
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
import type { AppButtonSize } from '../app/types/control'

export type AppTemplateActionsProps = {
  actions?: AppTemplateAction[]
  size?: AppButtonSize
  fullWidth?: boolean
}

const props = withDefaults(defineProps<AppTemplateActionsProps>(), {
  actions: () => [],
  fullWidth: false,
})

const actionsLoading = ref<number[]>([])
const toast = useToast()

const visibleActions = computed(() => props.actions.filter((action) => !action.hidden))

const getButtonProps = (action: AppTemplateAction, index: number) => {
  const {
    action: _action,
    hidden: _hidden,
    mode = 'both',
    class: _class,
    successNotification: _success,
    errorNotification: _error,
    ...button
  } = action
  return {
    ...button,
    label: mode === 'icon' ? undefined : action.label,
    // Icon-only actions keep their label as the accessible name.
    'aria-label': mode === 'icon' ? action.label : undefined,
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
      toast.default(action.successNotification)
    }
  } catch (error) {
    if (action.errorNotification) {
      toast.error(action.errorNotification)
    }
    throw error
  } finally {
    actionsLoading.value = actionsLoading.value.filter((value) => value !== index)
  }
}
</script>
