<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { DropdownMenuContentEmits, DropdownMenuContentProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { DropdownMenuContent, DropdownMenuPortal, useForwardPropsEmits } from 'reka-ui'
import { OVERLAY_MOTION_CLASS, OVERLAY_SURFACE_CLASS } from '~/shared/lib/overlay'
import { cn } from '~/shared/lib/utils'

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<DropdownMenuContentProps & { class?: HTMLAttributes['class'] }>(), {
  sideOffset: 6,
})
const emits = defineEmits<DropdownMenuContentEmits>()
const delegatedProps = reactiveOmit(props, 'class')
const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <DropdownMenuPortal>
    <DropdownMenuContent
      v-bind="{ ...forwarded, ...$attrs }"
      :class="
        cn(OVERLAY_SURFACE_CLASS, OVERLAY_MOTION_CLASS, 'z-overlay min-w-56 overflow-hidden outline-none', props.class)
      "
    >
      <slot />
    </DropdownMenuContent>
  </DropdownMenuPortal>
</template>
