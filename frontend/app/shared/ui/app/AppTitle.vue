<script setup lang="ts">
import type { TitleSizeToken, WeightToken } from '../template/types/template-ui-tokens'
withDefaults(
  defineProps<{
    size?: TitleSizeToken
    weight?: WeightToken
    title?: string
    subtitle?: string
    as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'div'
  }>(),
  { size: 'lg', weight: 'semibold', as: 'h2' },
)
const sizes = { sm: 'text-sm', md: 'text-base', lg: 'text-xl', xl: 'text-2xl' }
const weights = {
  light: 'font-light',
  regular: 'font-normal',
  medium: 'font-medium',
  semibold: 'font-semibold',
  bold: 'font-bold',
  black: 'font-black',
}
</script>
<template>
  <div class="flex min-w-0 flex-col gap-1">
    <component
      :is="as"
      class="m-0 leading-tight tracking-tight [overflow-wrap:anywhere] text-foreground"
      :class="[sizes[size], weights[weight]]"
    >
      {{ title }}<slot />
    </component>
    <p
      v-if="subtitle"
      class="text-sm leading-5 text-muted-foreground"
    >
      {{ subtitle }}
    </p>
  </div>
</template>
