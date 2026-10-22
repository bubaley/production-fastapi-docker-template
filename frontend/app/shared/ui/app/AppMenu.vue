<script setup lang="ts">
import { useOverlayStack } from './useOverlayStack'
import { computed, ref, watch, type Component, type HTMLAttributes } from 'vue'
import AppIcon from './AppIcon.vue'
import { Check } from '@lucide/vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '~/shared/ui/shadcn/dropdown-menu'
import AppTitle from './AppTitle.vue'
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuSeparator,
} from '~/shared/ui/shadcn/context-menu'

export type AppMenuAction = {
  label: string
  value?: string
  key?: string
  hidden?: boolean
  loading?: boolean
  severity?: string
  action?: () => void | Promise<void>
  icon?: Component | string
  checked?: boolean
  disabled?: boolean
  destructive?: boolean
  separatorBefore?: boolean
}

const props = withDefaults(
  defineProps<{
    actions?: AppMenuAction[]
    context?: boolean
    modal?: boolean
    preventOpenAutoFocus?: boolean
    passiveTrigger?: boolean
    label?: string
    mode?: 'popover' | 'cursor'
    title?: string
    subtitle?: string
    align?: 'start' | 'center' | 'end'
    side?: 'top' | 'right' | 'bottom' | 'left'
    sideOffset?: number
    contentClass?: HTMLAttributes['class']
    disabled?: boolean
  }>(),
  {
    actions: () => [],
    modal: true,
    align: 'end',
    side: 'bottom',
    sideOffset: 6,
  },
)

const open = defineModel<boolean>('open', { default: false })
const model = defineModel<boolean>({ default: false })
watch(model, (value) => {
  open.value = value
})
watch(open, (value) => {
  model.value = value
})
const visibleActions = computed(() => props.actions.filter((action) => !action.hidden))
const loading = ref(false)
const { contentStyle: overlayStyle } = useOverlayStack(open)
const emit = defineEmits<{ select: [action: AppMenuAction] }>()
const close = () => (open.value = false)
async function selectAction(action: AppMenuAction) {
  if (loading.value || action.disabled || action.loading) return
  loading.value = true
  try {
    await action.action?.()
    emit('select', action)
  } finally {
    loading.value = false
  }
}
defineExpose({
  hide: close,
  show: () => {
    open.value = true
  },
  toggle: () => {
    open.value = !open.value
  },
})
</script>

<template>
  <component
    :is="context || mode === 'cursor' ? ContextMenu : DropdownMenu"
    v-model:open="open"
    v-bind="context || mode === 'cursor' ? {} : { modal }"
  >
    <component
      :is="context || mode === 'cursor' ? ContextMenuTrigger : DropdownMenuTrigger"
      as-child
      :disabled="disabled || passiveTrigger"
    >
      <slot
        name="trigger"
        :open="open"
      />
    </component>
    <component
      :is="context || mode === 'cursor' ? ContextMenuContent : DropdownMenuContent"
      :style="overlayStyle"
      v-bind="context || mode === 'cursor' ? {} : { align, side, sideOffset }"
      :class="['border-border bg-background text-foreground', contentClass]"
      @open-auto-focus="preventOpenAutoFocus && $event.preventDefault()"
    >
      <component
        :is="context || mode === 'cursor' ? ContextMenuLabel : DropdownMenuLabel"
        v-if="title || label || subtitle || $slots.title"
        class="px-2 py-2 font-normal"
      >
        <slot name="title">
          <AppTitle
            :title="title || label"
            :subtitle="subtitle"
            size="sm"
          />
        </slot>
      </component>
      <component
        :is="context || mode === 'cursor' ? ContextMenuSeparator : DropdownMenuSeparator"
        v-if="(title || label || subtitle || $slots.title) && actions.length"
        class="-mx-1 my-1 h-px bg-border"
      />
      <template
        v-for="action in visibleActions"
        :key="action.value || action.key || action.label"
      >
        <component
          :is="context || mode === 'cursor' ? ContextMenuSeparator : DropdownMenuSeparator"
          v-if="action.separatorBefore"
          class="-mx-1 my-1 h-px bg-border"
        />
        <component
          :is="context || mode === 'cursor' ? ContextMenuItem : DropdownMenuItem"
          :disabled="action.disabled || action.loading || loading"
          :role="action.checked !== undefined ? 'menuitemradio' : 'menuitem'"
          :aria-checked="action.checked"
          :class="
            action.destructive || action.severity === 'danger'
              ? 'text-destructive hover:text-destructive focus:bg-destructive/10 focus:text-destructive'
              : 'text-foreground/75 hover:text-foreground focus:text-foreground'
          "
          @select="selectAction(action)"
        >
          <slot
            name="action"
            :action="action"
          >
            <AppIcon
              v-if="action.icon"
              :icon="action.icon"
              aria-hidden="true"
            />
            <span class="flex-1">{{ action.label }}</span>
          </slot>
          <AppIcon
            v-if="action.checked"
            :icon="Check"
            class="ml-4 size-4"
            aria-hidden="true"
          />
        </component>
      </template>
      <slot :close="close" />
    </component>
  </component>
</template>
