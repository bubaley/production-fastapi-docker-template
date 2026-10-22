<script setup lang="ts">
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '~/shared/ui/shadcn/sheet'
import { computed } from 'vue'
import { useOverlayStack } from './useOverlayStack'

defineOptions({ inheritAttrs: false })
const props = withDefaults(
  defineProps<{
    side?: 'left' | 'right'
    width?: number
    overlay?: boolean
    title?: string
    description?: string
    closeLabel?: string
  }>(),
  { side: 'left', width: 280, title: 'Панель' },
)
const model = defineModel<boolean>({ default: false })
const overlayOpen = computed(() => !!props.overlay && model.value)
const { backdropStyle, contentStyle, isTop } = useOverlayStack(overlayOpen)
const shellTarget = '#app-shell-drawer'
</script>

<template>
  <Sheet
    v-if="overlay"
    v-model:open="model"
  >
    <SheetContent
      v-bind="$attrs"
      :side="side"
      :close-label="closeLabel"
      :style="{ width: `${width}px`, ...contentStyle }"
      :overlay-style="backdropStyle"
      class="block max-w-[100vw] overflow-y-auto bg-sidebar p-6 text-foreground sm:max-w-[100vw]"
      @interact-outside="!isTop && $event.preventDefault()"
    >
      <SheetTitle class="sr-only">{{ title || 'Панель' }}</SheetTitle>
      <SheetDescription class="sr-only">{{ description || 'Дополнительные параметры и действия.' }}</SheetDescription>
      <slot />
    </SheetContent>
  </Sheet>
  <Teleport
    v-else
    :to="shellTarget"
  >
    <Transition :name="`drawer-${side}`">
      <aside
        v-if="model"
        v-bind="$attrs"
        class="h-full min-h-0 shrink-0 overflow-auto border-border bg-background text-foreground"
        :style="{ width: `${width}px` }"
        :class="side === 'right' ? 'border-l' : 'border-r'"
      >
        <slot />
      </aside>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-left-enter-active,
.drawer-left-leave-active,
.drawer-right-enter-active,
.drawer-right-leave-active {
  transition: transform 300ms ease;
}
.drawer-left-enter-active,
.drawer-right-enter-active {
  transition-duration: 200ms;
}
.drawer-left-enter-from,
.drawer-left-leave-to {
  transform: translateX(-100%);
}
.drawer-right-enter-from,
.drawer-right-leave-to {
  transform: translateX(100%);
}
@media (prefers-reduced-motion: reduce) {
  .drawer-left-enter-active,
  .drawer-left-leave-active,
  .drawer-right-enter-active,
  .drawer-right-leave-active {
    transition: none;
  }
}
</style>
