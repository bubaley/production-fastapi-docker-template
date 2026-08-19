<template>
  <div
    v-if="$slots.trigger"
    ref="triggerRef"
    class="inline-flex shrink-0"
    @click="onTriggerClick"
    @contextmenu="onTriggerContextMenu"
  >
    <slot name="trigger" />
  </div>
  <Popover
    ref="popoverRef"
    class="min-w-52 overflow-hidden"
    :pt="{ content: { class: '!p-1' } }"
    @show="onShow"
    @hide="onHide"
  >
    <AppTitle
      v-if="heading || subtitle"
      class="px-2 py-1.5"
      size="md"
      :title="heading"
      :subtitle="subtitle"
    />
    <AppListActions
      v-if="hasActions"
      :actions="actions"
      @select="hide"
    />
    <slot v-else />
  </Popover>
</template>

<script setup lang="ts">
import type { PopoverMethods } from 'primevue/popover'
import type { AppListAction } from './AppListActions.vue'

export type { AppListAction }
export type AppMenuMode = 'popover' | 'cursor'

const props = withDefaults(
  defineProps<{
    actions?: AppListAction[]
    label?: string
    title?: string
    subtitle?: string
    mode?: AppMenuMode
    context?: boolean
  }>(),
  {
    actions: () => [],
    mode: 'popover',
    context: false,
  },
)

const visible = defineModel<boolean>({ default: false })
const slots = useSlots()
const popoverRef = ref<(PopoverMethods & { $el?: HTMLElement }) | null>(null)
const triggerRef = ref<HTMLElement | null>(null)
const cursorEl = ref<HTMLSpanElement | null>(null)
const syncing = ref(false)

const heading = computed(() => props.label || props.title)
const hasActions = computed(() => props.actions.some((action) => !action.hidden))

const hostEl = () => triggerRef.value || popoverRef.value?.$el?.parentElement || null

const cursorTarget = (event: MouseEvent) => {
  if (!cursorEl.value) {
    const el = document.createElement('span')
    el.setAttribute('aria-hidden', 'true')
    Object.assign(el.style, {
      position: 'fixed',
      width: '0px',
      height: '0px',
      pointerEvents: 'none',
    })
    document.body.appendChild(el)
    cursorEl.value = el
  }
  cursorEl.value.style.left = `${event.clientX}px`
  cursorEl.value.style.top = `${event.clientY}px`
  return cursorEl.value
}

const popoverTarget = (event?: Event) => {
  const mouse = event as MouseEvent | undefined
  if (props.mode === 'cursor' && mouse && Number.isFinite(mouse.clientX) && Number.isFinite(mouse.clientY)) {
    return cursorTarget(mouse)
  }
  return hostEl()
}

const show = (event?: Event) => {
  const target = popoverTarget(event)
  const ev = { currentTarget: target } as Event
  const wasVisible = visible.value
  popoverRef.value?.show(ev, target || undefined)
  if (!wasVisible) return
  nextTick(() => popoverRef.value?.alignOverlay())
}

const hide = () => popoverRef.value?.hide()

const toggle = (event?: Event) => {
  const target = popoverTarget(event)
  const ev = { currentTarget: target } as Event
  popoverRef.value?.toggle(ev, target || undefined)
}

const onShow = () => {
  syncing.value = true
  visible.value = true
  window.addEventListener('scroll', hide, true)
  nextTick(() => {
    syncing.value = false
  })
}

const onHide = () => {
  syncing.value = true
  visible.value = false
  window.removeEventListener('scroll', hide, true)
  nextTick(() => {
    syncing.value = false
  })
}

const onHostEvent = (event: Event) => {
  if (props.context) event.preventDefault()
  toggle(event)
}

const onTriggerClick = (event: MouseEvent) => {
  if (props.context) return
  toggle(event)
}

const onTriggerContextMenu = (event: MouseEvent) => {
  if (!props.context) return
  event.preventDefault()
  toggle(event)
}

watch(visible, (isVisible) => {
  if (syncing.value) return
  if (isVisible) {
    window.setTimeout(() => {
      if (visible.value) show()
    })
    return
  }
  hide()
})

onMounted(() => {
  if (slots.trigger) return
  if (props.mode === 'cursor' && !props.context) return
  hostEl()?.addEventListener(props.context ? 'contextmenu' : 'click', onHostEvent)
})

onBeforeUnmount(() => {
  hostEl()?.removeEventListener(props.context ? 'contextmenu' : 'click', onHostEvent)
  window.removeEventListener('scroll', hide, true)
  cursorEl.value?.remove()
  cursorEl.value = null
})

defineExpose({ show, hide, toggle })
</script>
