<template>
  <div
    :class="
      inModalFooter
        ? 'flex w-full flex-col-reverse gap-2 sm:w-auto sm:flex-row sm:items-center sm:justify-end'
        : ['flex items-center gap-2', { 'w-full *:flex-1': fullWidth }]
    "
  >
    <AppButton
      v-for="(action, index) in visibleActions"
      :key="index"
      v-bind="getButtonProps(action, index)"
      :class="inModalFooter ? ['w-full sm:w-auto', action.class] : action.class"
      @click="executeAction(action, index)"
    />
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import type { AppTemplateAction } from './types/template-types'
import type { AppButtonSize } from '../app/types/control'
import { IN_MODAL_FOOTER } from '../app/modalFooter'

export type AppTemplateActionsProps = {
  actions?: AppTemplateAction[]
  size?: AppButtonSize
  fullWidth?: boolean
}

const props = withDefaults(defineProps<AppTemplateActionsProps>(), {
  actions: () => [],
  fullWidth: false,
})

// In a modal footer the one dialog layout (stacked on phones, right-aligned from `sm`) wins over `fullWidth`/`fluid`.
const inModalFooter = inject(IN_MODAL_FOOTER, false)
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
    fluid: inModalFooter ? false : props.fullWidth || action.fluid,
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
