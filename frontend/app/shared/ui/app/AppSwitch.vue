<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { Switch } from '~/shared/ui/shadcn/switch'
import type { AppControlSize } from './types/control'

withDefaults(
  defineProps<{
    disabled?: boolean
    size?: AppControlSize
    variant?: 'default' | 'contrast'
    class?: HTMLAttributes['class']
  }>(),
  { size: 'default', variant: 'default' },
)

const sizeClasses: Record<AppControlSize, string> = {
  xs: 'h-[14px] w-[24px] p-[1px] [&_[data-slot=switch-thumb]]:size-[12px] data-[state=checked]:[&_[data-slot=switch-thumb]]:translate-x-[10px]',
  sm: 'h-[16px] w-[28px] p-[1.5px] [&_[data-slot=switch-thumb]]:size-[13px] data-[state=checked]:[&_[data-slot=switch-thumb]]:translate-x-[12px]',
  default:
    'h-[18px] w-[32px] p-[2px] [&_[data-slot=switch-thumb]]:size-[14px] data-[state=checked]:[&_[data-slot=switch-thumb]]:translate-x-[14px]',
  lg: 'h-[22px] w-[40px] p-[2px] [&_[data-slot=switch-thumb]]:size-[18px] data-[state=checked]:[&_[data-slot=switch-thumb]]:translate-x-[18px]',
}

const model = defineModel<boolean>({ default: false })
</script>

<template>
  <Switch
    v-model="model"
    :disabled="disabled"
    :class="[
      'border-0 [&_[data-slot=switch-thumb]]:shadow-none',
      sizeClasses[size],
      variant === 'contrast' &&
        'data-[state=checked]:bg-foreground data-[state=checked]:[&_[data-slot=switch-thumb]]:bg-background',
      $props.class,
    ]"
  />
</template>
