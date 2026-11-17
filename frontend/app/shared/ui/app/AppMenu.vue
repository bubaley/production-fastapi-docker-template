<script setup lang="ts">
import { useOverlayStack } from './useOverlayStack'
import { computed, ref, watch, type Component, type HTMLAttributes, type StyleValue } from 'vue'
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
import { Popover, PopoverContent, PopoverTrigger } from '~/shared/ui/shadcn/popover'
import { OVERLAY_SURFACE_CLASS } from '~/shared/lib/overlay'
import { cn } from '~/shared/lib/utils'

export type AppMenuAction = {
  label: string
  value?: string
  key?: string
  hidden?: boolean
  loading?: boolean
  action?: () => void | Promise<void>
  icon?: Component
  checked?: boolean
  disabled?: boolean
  destructive?: boolean
  separatorBefore?: boolean
}

const props = withDefaults(
  defineProps<{
    actions?: AppMenuAction[]
    context?: boolean
    /** Default: `true` for menus (outside content is inert while open), `false` for `popover`. */
    modal?: boolean
    preventOpenAutoFocus?: boolean
    passiveTrigger?: boolean
    label?: string
    /**
     * `menu`: a list of `actions` (menu roles, arrow keys, typeahead). `cursor`: the same list as a right-click menu
     * (also `context`). `popover`: free-form content in the default slot (`{ close }`) with `role="dialog"`: inputs,
     * pickers, forms; no menu keyboard handling, Escape closes and focus returns to the trigger.
     */
    mode?: 'menu' | 'popover' | 'cursor'
    /** Accessible name of the `popover` surface when it has no visible title. */
    ariaLabel?: string
    title?: string
    subtitle?: string
    align?: 'start' | 'center' | 'end'
    side?: 'top' | 'right' | 'bottom' | 'left'
    sideOffset?: number
    contentClass?: HTMLAttributes['class']
    contentStyle?: StyleValue
    collisionPadding?: number
    disabled?: boolean
  }>(),
  {
    actions: () => [],
    modal: undefined,
    mode: 'menu',
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
const emit = defineEmits<{ select: [action: AppMenuAction]; openAutoFocus: [event: Event] }>()
const kind = computed<'menu' | 'popover' | 'cursor'>(() => (props.context ? 'cursor' : props.mode))
const hasHeader = computed(() => Boolean(props.title || props.label || props.subtitle))
const surfaceClass = computed(() => cn(OVERLAY_SURFACE_CLASS, props.contentClass))
const surfaceStyle = computed<StyleValue>(() => [props.contentStyle, overlayStyle.value])
const onOpenAutoFocus = (event: Event) => {
  if (props.preventOpenAutoFocus) event.preventDefault()
  emit('openAutoFocus', event)
}
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
  <Popover
    v-if="kind === 'popover'"
    v-model:open="open"
    :modal="modal ?? false"
  >
    <PopoverTrigger
      as-child
      :disabled="disabled || passiveTrigger"
    >
      <slot
        name="trigger"
        :open="open"
      />
    </PopoverTrigger>
    <PopoverContent
      :style="surfaceStyle"
      :align="align"
      :side="side"
      :side-offset="sideOffset"
      :collision-padding="collisionPadding"
      :aria-label="ariaLabel || title || label"
      :class="cn('w-auto', surfaceClass)"
      @open-auto-focus="onOpenAutoFocus"
    >
      <template v-if="hasHeader || $slots.title">
        <div class="px-2 py-2">
          <slot name="title">
            <AppTitle
              :title="title || label"
              :subtitle="subtitle"
              size="sm"
            />
          </slot>
        </div>
        <div class="-mx-1.5 my-1 h-px bg-border" />
      </template>
      <slot :close="close" />
    </PopoverContent>
  </Popover>
  <component
    :is="kind === 'cursor' ? ContextMenu : DropdownMenu"
    v-else
    v-model:open="open"
    v-bind="kind === 'cursor' ? {} : { modal: modal ?? true }"
  >
    <component
      :is="kind === 'cursor' ? ContextMenuTrigger : DropdownMenuTrigger"
      as-child
      :disabled="disabled || passiveTrigger"
    >
      <slot
        name="trigger"
        :open="open"
      />
    </component>
    <component
      :is="kind === 'cursor' ? ContextMenuContent : DropdownMenuContent"
      :style="surfaceStyle"
      v-bind="kind === 'cursor' ? { collisionPadding } : { align, side, sideOffset, collisionPadding }"
      :class="surfaceClass"
      @open-auto-focus="onOpenAutoFocus"
    >
      <component
        :is="kind === 'cursor' ? ContextMenuLabel : DropdownMenuLabel"
        v-if="hasHeader || $slots.title"
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
        :is="kind === 'cursor' ? ContextMenuSeparator : DropdownMenuSeparator"
        v-if="(hasHeader || $slots.title) && actions.length"
        class="-mx-1 my-1 h-px bg-border"
      />
      <template
        v-for="action in visibleActions"
        :key="action.value || action.key || action.label"
      >
        <component
          :is="kind === 'cursor' ? ContextMenuSeparator : DropdownMenuSeparator"
          v-if="action.separatorBefore"
          class="-mx-1 my-1 h-px bg-border"
        />
        <component
          :is="kind === 'cursor' ? ContextMenuItem : DropdownMenuItem"
          :disabled="action.disabled || action.loading || loading"
          :role="action.checked !== undefined ? 'menuitemradio' : 'menuitem'"
          :aria-checked="action.checked"
          :class="
            action.destructive
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
