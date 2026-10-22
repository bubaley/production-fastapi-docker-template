<script setup lang="ts">
import type { DialogContentEmits, DialogContentProps } from 'reka-ui'
import type { HTMLAttributes, StyleValue } from 'vue'
import { X } from '@lucide/vue'
import { reactiveOmit } from '@vueuse/core'
import { DialogClose, DialogContent, DialogOverlay, DialogPortal, useForwardPropsEmits } from 'reka-ui'
import { cn } from '~/shared/lib/utils'

defineOptions({ inheritAttrs: false })
const props = defineProps<
  DialogContentProps & {
    class?: HTMLAttributes['class']
    style?: StyleValue
    overlayClass?: HTMLAttributes['class']
    overlayStyle?: StyleValue
    showClose?: boolean
    closeLabel?: string
    motion?: 'modal' | 'left' | 'right'
  }
>()
const emits = defineEmits<DialogContentEmits>()
const delegatedProps = reactiveOmit(props, 'class', 'style', 'overlayClass', 'overlayStyle', 'showClose', 'closeLabel', 'motion')
const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <DialogPortal>
    <DialogOverlay
      :style="overlayStyle"
      :class="
        cn(
          'fixed inset-0 z-[var(--app-overlay-z,1000)] bg-black/55 backdrop-blur-[3px] data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          overlayClass
        )
      "
    />
    <DialogContent
      v-bind="{ ...forwarded, ...$attrs }"
      :style="props.style"
      :class="
        cn(
          'fixed left-1/2 top-1/2 z-[var(--app-overlay-z,1010)] grid w-[calc(100%_-_2rem)] max-h-[calc(100dvh-2rem)] overflow-y-auto max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl border border-overlay-border bg-background p-6 text-card-foreground outline-none shadow-xl duration-200 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          props.motion === 'left' ? 'data-[state=open]:slide-in-from-left data-[state=closed]:slide-out-to-left duration-300 data-[state=open]:duration-200' : props.motion === 'right' ? 'data-[state=open]:slide-in-from-right data-[state=closed]:slide-out-to-right duration-300 data-[state=open]:duration-200' : 'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          props.class
        )
      "
    >
      <slot />
      <DialogClose
        v-if="showClose !== false"
        class="absolute right-4 top-4 rounded-sm text-muted-foreground opacity-80 transition-opacity hover:text-foreground hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none"
      >
        <X class="size-4" />
        <span class="sr-only">{{ closeLabel || 'Закрыть' }}</span>
      </DialogClose>
    </DialogContent>
  </DialogPortal>
</template>
