<template>
  <Popover ref="op">
    <AppTitle
      v-if="title || subtitle"
      size="normal"
      :title="title"
      :subtitle="subtitle"
    />
    <slot />
  </Popover>
</template>

<script setup lang="ts">
import type { PopoverMethods, PopoverProps } from 'primevue/popover'

export interface CPopoverProps extends /* @vue-ignore */ PopoverProps {
  test?: string
  title?: string
  subtitle?: string
}

withDefaults(defineProps<CPopoverProps>(), {})

const op = ref<(PopoverMethods & { $el: HTMLElement }) | null>()

const _getParent = () => {
  return op.value?.$el.parentElement
}

function handleClick(e: Event) {
  op.value?.toggle(e)
}

onMounted(() => {
  const parent = _getParent()
  if (parent) parent.addEventListener('click', handleClick)
})

onBeforeUnmount(() => {
  const parent = _getParent()
  if (parent) parent.removeEventListener('click', handleClick)
})
</script>
