<script setup lang="ts">
import type { DialogContentEmits, DialogContentProps } from 'reka-ui'
import type { HTMLAttributes, StyleValue } from 'vue'
import { X } from '@lucide/vue'
import { reactiveOmit } from '@vueuse/core'
import { cn } from '~/shared/lib/utils'
import { DialogClose, DialogContent, DialogPortal, useForwardPropsEmits } from 'reka-ui'
import SheetOverlay from './SheetOverlay.vue'

interface SheetContentProps extends DialogContentProps {
  class?: HTMLAttributes['class']
  side?: 'top' | 'right' | 'bottom' | 'left'
  overlayClass?: HTMLAttributes['class']
  overlayStyle?: StyleValue
  showClose?: boolean
  closeLabel?: string
}

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(defineProps<SheetContentProps>(), {
  side: 'right',
  showClose: true,
  closeLabel: 'Закрыть',
})
const emits = defineEmits<DialogContentEmits>()

const delegatedProps = reactiveOmit(props, 'class', 'side', 'overlayClass', 'overlayStyle', 'showClose', 'closeLabel')

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <DialogPortal>
    <SheetOverlay
      :class="overlayClass"
      :style="overlayStyle"
    />
    <DialogContent
      data-slot="sheet-content"
      :class="
        cn(
          'fixed z-overlay flex flex-col gap-4 bg-background shadow-lg transition ease-in-out outline-none data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:animate-in data-[state=open]:duration-200',
          side === 'right' &&
            'inset-y-0 right-0 h-full w-3/4 border-l data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right sm:max-w-sm',
          side === 'left' &&
            'inset-y-0 left-0 h-full w-3/4 border-r data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left sm:max-w-sm',
          side === 'top' &&
            'inset-x-0 top-0 h-auto border-b data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top',
          side === 'bottom' &&
            'inset-x-0 bottom-0 h-auto border-t data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom',
          props.class,
        )
      "
      v-bind="{ ...$attrs, ...forwarded }"
    >
      <slot />

      <DialogClose
        v-if="showClose"
        class="absolute top-4 right-4 rounded-sm text-muted-foreground opacity-80 transition-opacity hover:text-foreground hover:opacity-100 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none disabled:pointer-events-none"
      >
        <X class="size-4" />
        <span class="sr-only">{{ closeLabel }}</span>
      </DialogClose>
    </DialogContent>
  </DialogPortal>
</template>
