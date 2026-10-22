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
const delegatedProps = reactiveOmit(
  props,
  'class',
  'style',
  'overlayClass',
  'overlayStyle',
  'showClose',
  'closeLabel',
  'motion',
)
const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <DialogPortal>
    <DialogOverlay
      :style="overlayStyle"
      :class="
        cn(
          'fixed inset-0 z-[var(--app-overlay-z,1000)] bg-black/55 backdrop-blur-[3px] data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0',
          overlayClass,
        )
      "
    />
    <DialogContent
      v-bind="{ ...forwarded, ...$attrs }"
      :style="props.style"
      :class="
        cn(
          'fixed top-1/2 left-1/2 z-[var(--app-overlay-z,1010)] grid max-h-[calc(100dvh-2rem)] w-[calc(100%_-_2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 overflow-y-auto rounded-xl border border-overlay-border bg-background p-6 text-card-foreground shadow-xl duration-200 outline-none data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0',
          props.motion === 'left'
            ? 'duration-300 data-[state=closed]:slide-out-to-left data-[state=open]:duration-200 data-[state=open]:slide-in-from-left'
            : props.motion === 'right'
              ? 'duration-300 data-[state=closed]:slide-out-to-right data-[state=open]:duration-200 data-[state=open]:slide-in-from-right'
              : 'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          props.class,
        )
      "
    >
      <slot />
      <DialogClose
        v-if="showClose !== false"
        class="absolute top-4 right-4 rounded-sm text-muted-foreground opacity-80 transition-opacity hover:text-foreground hover:opacity-100 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none disabled:pointer-events-none"
      >
        <X class="size-4" />
        <span class="sr-only">{{ closeLabel || 'Закрыть' }}</span>
      </DialogClose>
    </DialogContent>
  </DialogPortal>
</template>
