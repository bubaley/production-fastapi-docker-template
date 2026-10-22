<script setup lang="ts">
import { TabsContent } from '~/shared/ui/shadcn/tabs'
defineProps<{ tabValue: string }>()
</script>
<template>
  <TabsContent
    :value="tabValue"
    class="min-w-0"
  >
    <slot />
  </TabsContent>
</template>
