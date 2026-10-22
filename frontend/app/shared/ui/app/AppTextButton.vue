<template>
  <component
    :is="to ? RouterLink : 'button'"
    :type="to ? undefined : 'button'"
    :to="to"
    class="inline-flex cursor-pointer items-center gap-1.5 rounded-sm border-0 bg-transparent p-0 text-left transition-[filter] select-none hover:brightness-90 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
    :class="[weight && weightClasses[weight], toneVariants({ tone }), underline && 'hover:underline']"
    @click="handleClick"
  >
    <AppIcon
      v-if="icon"
      :icon="icon"
      size="sm"
    />
    <span>{{ label }}<slot /></span>
  </component>
</template>

<script lang="ts" setup>
import type { Component } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import { useClipboard } from '@vueuse/core'
import { toneVariants, type Tone } from './tone'

const props = withDefaults(
  defineProps<{
    label?: string
    weight?: WeightToken
    tone?: Tone
    icon?: Component
    to?: string | RouteLocationRaw
    copied?: boolean
    value?: any
    underline?: boolean
  }>(),
  {
    tone: 'primary',
    underline: true,
  },
)

const weightClasses: Record<WeightToken, string> = {
  light: 'font-light',
  regular: 'font-normal',
  medium: 'font-medium',
  semibold: 'font-semibold',
  bold: 'font-bold',
  black: 'font-black',
}

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()
const { copy } = useClipboard()
const toast = useToast()

const handleClick = (event: MouseEvent) => {
  if (props.copied) {
    copyValue()
    return
  }
  emit('click', event)
}

const copyValue = () => {
  if (props.label || props.value) {
    copy(props.value || props.label)
    toast.default('Скопировано')
  }
}
</script>
