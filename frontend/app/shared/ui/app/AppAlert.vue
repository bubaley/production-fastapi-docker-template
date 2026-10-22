<script setup lang="ts">
import { computed, type Component } from 'vue'
import { CircleAlert, CircleCheck, Info, TriangleAlert } from '@lucide/vue'
import { Alert, AlertDescription, AlertTitle } from '~/shared/ui/shadcn/alert'
import { toneVariants, type Tone } from './tone'

const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    tone?: Extract<Tone, 'neutral' | 'info' | 'success' | 'warning' | 'destructive'>
    icon?: Component | null
  }>(),
  { tone: 'info', icon: undefined },
)
const defaultIcons = {
  neutral: Info,
  info: Info,
  success: CircleCheck,
  warning: TriangleAlert,
  destructive: CircleAlert,
}
const resolvedIcon = computed(() => (props.icon === null ? undefined : props.icon || defaultIcons[props.tone]))
</script>

<template>
  <Alert
    :role="tone === 'destructive' || tone === 'warning' ? 'alert' : 'status'"
    :class="toneVariants({ tone, appearance: 'tinted' })"
  >
    <component
      :is="resolvedIcon"
      v-if="resolvedIcon"
      :class="toneVariants({ tone })"
      aria-hidden="true"
    />
    <AlertTitle v-if="title">{{ title }}</AlertTitle>
    <AlertDescription v-if="description || $slots.default">
      <slot>{{ description }}</slot>
    </AlertDescription>
  </Alert>
</template>
