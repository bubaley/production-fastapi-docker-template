<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { TabsListProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { TabsList } from 'reka-ui'
import { cn } from '~/shared/lib/utils'

const props = defineProps<TabsListProps & { class?: HTMLAttributes['class'] }>()
const delegatedProps = reactiveOmit(props, 'class')
</script>

<template>
  <TabsList
    v-bind="delegatedProps"
    :class="
      cn(
        'inline-flex h-9 items-center gap-0.5 rounded-md border border-border bg-muted p-0.5 text-muted-foreground',
        props.class
      )
    "
  >
    <slot />
  </TabsList>
</template>
