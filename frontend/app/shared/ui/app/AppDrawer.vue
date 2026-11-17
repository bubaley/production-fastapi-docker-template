<script setup lang="ts">
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '~/shared/ui/shadcn/sheet'
import type { HTMLAttributes } from 'vue'
import { cn } from '~/shared/lib/utils'
import { useOverlayStack } from './useOverlayStack'

/** Side panel over the page (a sheet with a backdrop); takes part in the overlay stack like modals and menus. */
defineOptions({ inheritAttrs: false })
withDefaults(
  defineProps<{
    side?: 'left' | 'right'
    width?: number
    title?: string
    description?: string
    closeLabel?: string
    /** The corner close button (Escape and the backdrop still close it). */
    closeable?: boolean
    /** Classes merged last into the sheet (e.g. `p-0` for a full-bleed panel). */
    contentClass?: HTMLAttributes['class']
  }>(),
  { side: 'left', width: 280, title: 'Панель', closeable: true },
)
const model = defineModel<boolean>({ default: false })
const { backdropStyle, contentStyle, isTop } = useOverlayStack(model)
</script>

<template>
  <Sheet v-model:open="model">
    <SheetContent
      v-bind="$attrs"
      :side="side"
      :close-label="closeLabel"
      :show-close="closeable"
      :style="{ width: `${width}px`, ...contentStyle }"
      :overlay-style="backdropStyle"
      :class="cn('block max-w-[100vw] overflow-y-auto bg-sidebar p-6 text-foreground sm:max-w-[100vw]', contentClass)"
      @interact-outside="!isTop && $event.preventDefault()"
    >
      <SheetTitle class="sr-only">{{ title || 'Панель' }}</SheetTitle>
      <SheetDescription class="sr-only">{{ description || 'Дополнительные параметры и действия.' }}</SheetDescription>
      <slot />
    </SheetContent>
  </Sheet>
</template>
