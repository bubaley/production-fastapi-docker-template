<script setup lang="ts">
import { computed } from 'vue'
import { LoaderCircle } from '@lucide/vue'
import AppIcon, { type AppIconSize } from './AppIcon.vue'

export type AppLoadingIndicatorProps = {
  label?: string
  locale?: 'ru' | 'en'
  size?: 'sm' | 'md'
  fluid?: boolean
}

const props = withDefaults(defineProps<AppLoadingIndicatorProps>(), {
  locale: 'ru',
  size: 'sm',
  fluid: false,
})

const text = computed(() => props.label || (props.locale === 'en' ? 'Loading…' : 'Загрузка…'))
const iconSize = computed<AppIconSize>(() => (props.size === 'md' ? 'sm' : 'xs'))
</script>

<template>
  <span
    role="status"
    aria-live="polite"
    class="items-center justify-center text-muted-foreground"
    :class="[fluid ? 'flex w-full' : 'inline-flex', size === 'md' ? 'gap-2 text-sm' : 'gap-1.5 text-xs']"
  >
    <AppIcon
      :icon="LoaderCircle"
      :size="iconSize"
      class="animate-spin motion-reduce:animate-none"
    />
    <span>{{ text }}</span>
  </span>
</template>
