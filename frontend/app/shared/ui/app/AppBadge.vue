<script setup lang="ts">
import type { Component } from 'vue'
import { Badge } from '~/shared/ui/shadcn/badge'
import { toneVariants, type Tone } from './tone'

withDefaults(
  defineProps<{
    label?: string
    tone?: Tone
    variant?: 'solid' | 'soft' | 'outline'
    icon?: Component
  }>(),
  { tone: 'neutral', variant: 'soft' },
)
</script>

<template>
  <Badge
    variant="outline"
    :class="[variant !== 'outline' && 'border-transparent', toneVariants({ tone, appearance: variant })]"
  >
    <AppIcon
      v-if="icon"
      :icon="icon"
      size="xs"
    />
    <slot>{{ label }}</slot>
  </Badge>
</template>
