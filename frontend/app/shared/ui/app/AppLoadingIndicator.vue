<script setup lang="ts">
import { computed } from 'vue'
import { LoaderCircle } from '@lucide/vue'
import AppIcon from './AppIcon.vue'

/**
 * The one loading state for data: a small spinner on the left and a muted `text-sm` line. Tables, lists, templates,
 * infinite scroll, selects and pickers all render this component, so its look changes in one place.
 */
export type AppLoadingIndicatorProps = {
  label?: string
  locale?: 'ru' | 'en'
  /** Fill the container's width and center the indicator in it. */
  fluid?: boolean
}

const props = withDefaults(defineProps<AppLoadingIndicatorProps>(), {
  locale: 'ru',
  fluid: false,
})

const text = computed<string>(() => props.label || (props.locale === 'en' ? 'Loading…' : 'Загрузка…'))
</script>

<template>
  <span
    role="status"
    aria-live="polite"
    class="items-center justify-center gap-2 text-sm text-muted-foreground"
    :class="fluid ? 'flex w-full' : 'inline-flex'"
  >
    <AppIcon
      :icon="LoaderCircle"
      size="sm"
      class="shrink-0 animate-spin motion-reduce:animate-none"
    />
    <span>{{ text }}</span>
  </span>
</template>
