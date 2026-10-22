<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { ContextMenuItemEmits, ContextMenuItemProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { ContextMenuItem, useForwardPropsEmits } from 'reka-ui'
import { cn } from '~/shared/lib/utils'

const props = defineProps<ContextMenuItemProps & { class?: HTMLAttributes['class'] }>()
const emits = defineEmits<ContextMenuItemEmits>()
const delegatedProps = reactiveOmit(props, 'class')
const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <ContextMenuItem
    v-bind="forwarded"
    :class="
      cn(
        'relative flex h-9 cursor-pointer items-center gap-2 rounded-md px-2.5 text-[13px] transition-colors outline-none select-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-40 [&_svg]:size-4 [&_svg]:shrink-0',
        props.class,
      )
    "
  >
    <slot />
  </ContextMenuItem>
</template>
