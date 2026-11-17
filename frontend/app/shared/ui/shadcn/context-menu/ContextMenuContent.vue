<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { ContextMenuContentEmits, ContextMenuContentProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { ContextMenuContent, ContextMenuPortal, useForwardPropsEmits } from 'reka-ui'
import { OVERLAY_MOTION_CLASS, OVERLAY_SURFACE_CLASS } from '~/shared/lib/overlay'
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
        cn(OVERLAY_SURFACE_CLASS, OVERLAY_MOTION_CLASS, 'z-overlay min-w-56 overflow-hidden outline-none', props.class)
      "
    >
      <slot />
    </ContextMenuContent>
  </ContextMenuPortal>
</template>
