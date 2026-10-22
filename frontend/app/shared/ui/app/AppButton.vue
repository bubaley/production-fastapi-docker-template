<script setup lang="ts">
import { computed, useSlots, type Component, type HTMLAttributes } from 'vue'
import { useRouter, type RouteLocationRaw } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { LoaderCircle } from '@lucide/vue'
import { Button, type ButtonVariants } from '~/shared/ui/shadcn/button'
import {
  activeOutlineClasses,
  appControlRadiusClasses,
  appControlStyles,
  appControlIconSize,
  type AppButtonSize
} from './types/control'

export type AppButtonProps = {
  onClick?: (event: MouseEvent) => void
  to?: RouteLocationRaw
  severity?: 'primary' | 'secondary' | 'success' | 'info' | 'warn' | 'warning' | 'danger' | 'help' | 'contrast'
  outlined?: boolean
  text?: boolean
  rounded?: boolean
  hidden?: boolean
  iconPos?: 'left' | 'right'
  iconSize?: number
  label?: string
  textVariant?: 'base' | 'muted'
  variant?: ButtonVariants['variant'] | 'active-outline' | 'outlined' | 'text'
  size?: AppButtonSize | 'small' | 'large'
  icon?: Component | string
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
  size: 'default',
  iconPosition: 'start',
  type: 'button'
})
const router = useRouter()
const slots = useSlots()
const emit = defineEmits<{ click: [event: MouseEvent] }>()
const controlSize = computed(() => props.size === 'small' ? 'sm' : props.size === 'large' ? 'lg' : props.icon && !props.label && !slots.default && props.size === 'default' ? 'icon' : props.size)
const buttonVariant = computed(() => props.text || props.variant === 'text' ? 'ghost' : props.outlined || props.variant === 'outlined' || props.variant === 'active-outline' ? 'outline' : props.severity === 'danger' ? 'destructive' : props.severity === 'secondary' ? 'secondary' : props.variant)
const textVariantClasses = computed(() => {
  if (props.textVariant !== 'muted') return undefined
  const hoverClass = buttonVariant.value === 'primary'
    ? 'hover:text-primary-foreground focus-visible:text-primary-foreground'
    : buttonVariant.value === 'default' || buttonVariant.value === 'destructive'
      ? 'hover:text-background focus-visible:text-background'
      : buttonVariant.value === 'link'
        ? 'hover:text-primary focus-visible:text-primary'
        : buttonVariant.value === 'secondary'
          ? 'hover:text-secondary-foreground focus-visible:text-secondary-foreground'
          : 'hover:text-foreground focus-visible:text-foreground'
  return ['text-muted-foreground', hoverClass]
})
function handleClick(event: MouseEvent) { emit('click', event); if (props.to) void router.push(props.to) }
</script>

<template>
  <Button
    class="cursor-pointer disabled:cursor-not-allowed disabled:pointer-events-auto"
    :type="type"
    :variant="buttonVariant"
    :size="controlSize"
    :style="appControlStyles.button[controlSize]"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
    :class="[
      appControlRadiusClasses[controlSize],
      textVariantClasses,
      fluid && 'w-full',
      variant === 'ghost' && 'hover:bg-[color:var(--ds-field-hover)]',
      variant === 'active-outline' && activeOutlineClasses
    ]"
    @click="handleClick"
  >
    <AppIcon
      v-if="loading"
      :size="appControlIconSize[controlSize]"
      :icon="LoaderCircle"
      :class="['animate-spin', iconClass]"
      aria-hidden="true"
    />
    <AppIcon
      v-else-if="icon && iconPos !== 'right' && iconPosition === 'start'"
      :size="appControlIconSize[controlSize]"
      :icon="icon"
      :class="iconClass"
      aria-hidden="true"
    />
    <slot>{{ label }}</slot>
    <AppIcon
      v-if="icon && (iconPos === 'right' || iconPosition === 'end') && !loading"
      :size="appControlIconSize[controlSize]"
      :icon="icon"
      :class="iconClass"
      aria-hidden="true"
    />
  </Button>
</template>
