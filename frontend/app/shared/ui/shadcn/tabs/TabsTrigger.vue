<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { TabsTriggerProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { TabsTrigger } from 'reka-ui'
import { cn } from '~/shared/lib/utils'

const props = defineProps<TabsTriggerProps & { class?: HTMLAttributes['class'] }>()
const delegatedProps = reactiveOmit(props, 'class')
</script>

<template>
  <TabsTrigger
    v-bind="delegatedProps"
    :class="
      cn(
        'inline-flex h-7 items-center justify-center whitespace-nowrap rounded-[5px] px-3 text-xs font-medium outline-none transition-colors hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40 data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm',
        props.class
      )
    "
  >
    <slot />
  </TabsTrigger>
</template>
