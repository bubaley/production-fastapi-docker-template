<script setup lang="ts">
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '~/shared/ui/shadcn/dialog'
import { computed } from 'vue'
import { useOverlayStack } from './useOverlayStack'

defineOptions({ inheritAttrs: false })
const props = withDefaults(
  defineProps<{ side?: 'left' | 'right'; width?: number; overlay?: boolean; title?: string; description?: string; closeLabel?: string }>(),
  { side: 'left', width: 280, title: 'Панель' }
)
const model = defineModel<boolean>({ default: false })
const overlayOpen = computed(() => !!props.overlay && model.value)
const { backdropStyle, contentStyle, isTop } = useOverlayStack(overlayOpen)
const shellTarget = '#app-shell-drawer'
</script>

<template>
  <Dialog
    v-if="overlay"
    v-model:open="model"
  >
    <DialogContent
      v-bind="$attrs"
      :close-label="closeLabel"
      :motion="side"
      :style="{ width: `${width}px`, ...contentStyle }"
      :overlay-style="backdropStyle"
      :class="[
        'inset-y-0 max-h-dvh max-w-[100vw] translate-x-0 translate-y-0 rounded-none border-0 bg-[var(--ds-sidebar)] text-foreground',
        side === 'right' ? 'left-auto right-0 border-l border-border' : 'left-0 right-auto border-r border-border'
      ]"
      @interact-outside="!isTop && $event.preventDefault()"
    >
      <DialogTitle class="sr-only">{{ title || 'Панель' }}</DialogTitle>
      <DialogDescription class="sr-only">{{ description || 'Дополнительные параметры и действия.' }}</DialogDescription>
      <div><slot /></div>
    </DialogContent>
  </Dialog>
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
.drawer-left-enter-active, .drawer-left-leave-active,
.drawer-right-enter-active, .drawer-right-leave-active {
  transition: transform 300ms ease;
}
.drawer-left-enter-active, .drawer-right-enter-active { transition-duration: 200ms; }
.drawer-left-enter-from, .drawer-left-leave-to { transform: translateX(-100%); }
.drawer-right-enter-from, .drawer-right-leave-to { transform: translateX(100%); }
@media (prefers-reduced-motion: reduce) {
  .drawer-left-enter-active, .drawer-left-leave-active,
  .drawer-right-enter-active, .drawer-right-leave-active { transition: none; }
}
</style>
