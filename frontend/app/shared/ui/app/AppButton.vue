<script setup lang="ts">
import { computed, resolveComponent, useAttrs, useSlots, type Component, type HTMLAttributes } from 'vue'
import { useRouter, type RouteLocationRaw } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { Button } from '~/shared/ui/shadcn/button'
import { appControlIconSize, type AppButtonSize } from './types/control'
import {
  appButtonExtraClasses,
  appButtonPrimitiveSize,
  resolveAppButtonSize,
  type AppButtonTextVariant,
  type AppButtonVariant,
} from './appButton'

export type AppButtonProps = {
  onClick?: (event: MouseEvent) => void
  to?: RouteLocationRaw
  /** Renders a real link styled as a button (`NuxtLink`): downloads, public pages, other sites. */
  href?: string
  /** With `href`: opens it in a new tab with `rel="noopener noreferrer"`. */
  external?: boolean
  label?: string
  variant?: AppButtonVariant
  size?: AppButtonSize
  textVariant?: AppButtonTextVariant
  /** A Lucide component. Icon-only buttons must have `aria-label` (or `title`). */
  icon?: Component
  iconClass?: HTMLAttributes['class']
  iconPosition?: 'start' | 'end'
  loading?: boolean
  disabled?: boolean
  fluid?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<AppButtonProps>(), {
  variant: 'default',
  textVariant: 'base',
  size: 'md',
  iconPosition: 'start',
  type: 'button',
})
const router = useRouter()
const slots = useSlots()
const attrs = useAttrs()
const emit = defineEmits<{ click: [event: MouseEvent] }>()
const iconOnly = computed(() => Boolean(props.icon) && !props.label && !slots.default)
const controlSize = computed(() => resolveAppButtonSize(props.size, iconOnly.value))
if (import.meta.dev && iconOnly.value && !attrs['aria-label'] && !attrs['aria-labelledby'] && !attrs.title) {
  console.warn('[AppButton] Icon-only buttons need an accessible name: pass `aria-label` or `title`.')
}
// A disabled or loading link falls back to a disabled button: anchors cannot be disabled.
const isLink = computed(() => Boolean(props.href) && !props.disabled && !props.loading)
// Nuxt compiles the literal `resolveComponent('NuxtLink')` into a direct import; resolving it only for links keeps
// plain buttons free of the lookup (and of "failed to resolve" warnings in unit tests without Nuxt).
const linkComponent = props.href ? resolveComponent('NuxtLink') : 'a'
const rootProps = computed(() =>
  isLink.value
    ? {
        as: linkComponent,
        href: props.href,
        external: props.external || undefined,
        target: props.external ? '_blank' : undefined,
        rel: props.external ? 'noopener noreferrer' : undefined,
      }
    : {
        as: 'button',
        type: props.type,
        disabled: props.disabled || props.loading,
        'aria-busy': props.loading || undefined,
      },
)
function handleClick(event: MouseEvent) {
  emit('click', event)
  if (props.to && !isLink.value) void router.push(props.to)
}
</script>

<template>
  <Button
    v-bind="rootProps"
    :variant="variant"
    :size="appButtonPrimitiveSize(controlSize)"
    :class="appButtonExtraClasses({ variant, textVariant, fluid })"
    @click="handleClick"
  >
    <AppIcon
      v-if="loading"
      :size="appControlIconSize[controlSize]"
      loading
      :class="iconClass"
    />
    <AppIcon
      v-else-if="icon && iconPosition === 'start'"
      :size="appControlIconSize[controlSize]"
      :icon="icon"
      :class="iconClass"
    />
    <slot>{{ label }}</slot>
    <AppIcon
      v-if="icon && iconPosition === 'end' && !loading"
      :size="appControlIconSize[controlSize]"
      :icon="icon"
      :class="iconClass"
    />
  </Button>
</template>
