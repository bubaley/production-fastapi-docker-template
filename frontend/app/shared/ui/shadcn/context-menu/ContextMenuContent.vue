<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { ContextMenuContentEmits, ContextMenuContentProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { ContextMenuContent, ContextMenuPortal, useForwardPropsEmits } from 'reka-ui'
import { cn } from '~/shared/lib/utils'

defineOptions({ inheritAttrs: false })

const props = defineProps<ContextMenuContentProps & { class?: HTMLAttributes['class'] }>()
const emits = defineEmits<ContextMenuContentEmits>()
const delegatedProps = reactiveOmit(props, 'class')
const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <ContextMenuPortal>
    <ContextMenuContent
      v-bind="{ ...forwarded, ...$attrs }"
      :class="
        cn(
          'z-overlay min-w-56 overflow-hidden rounded-lg border border-border-strong bg-popover p-1.5 text-popover-foreground shadow-overlay outline-none data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95',
          props.class,
        )
      "
    >
      <slot />
    </ContextMenuContent>
  </ContextMenuPortal>
</template>
