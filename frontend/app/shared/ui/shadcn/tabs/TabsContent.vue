<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { TabsContentProps } from 'reka-ui'
import { reactiveOmit } from '@vueuse/core'
import { TabsContent } from 'reka-ui'
import { cn } from '~/shared/lib/utils'

const props = defineProps<TabsContentProps & { class?: HTMLAttributes['class'] }>()
const delegatedProps = reactiveOmit(props, 'class')
</script>

<template>
  <TabsContent
    v-bind="delegatedProps"
    :class="cn('mt-4 outline-none focus-visible:ring-2 focus-visible:ring-ring', props.class)"
  >
    <slot />
  </TabsContent>
</template>
