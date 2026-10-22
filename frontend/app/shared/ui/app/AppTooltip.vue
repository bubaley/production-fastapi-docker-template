<script setup lang="ts">
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '~/shared/ui/shadcn/tooltip'

withDefaults(
  defineProps<{
    /** Plain-text content; use the default slot for rich content. */
    text?: string
    side?: 'top' | 'right' | 'bottom' | 'left'
    delay?: number
    disabled?: boolean
  }>(),
  { side: 'top', delay: 300 },
)
</script>

<template>
  <TooltipProvider :delay-duration="delay">
    <Tooltip :disabled="disabled">
      <TooltipTrigger as-child>
        <slot name="trigger" />
      </TooltipTrigger>
      <TooltipContent
        :side="side"
        class="max-w-xs"
      >
        <slot>{{ text }}</slot>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
</template>
