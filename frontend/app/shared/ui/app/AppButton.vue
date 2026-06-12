<template>
  <div>
    <component
      :is="to ? 'router-link' : 'div'"
      v-bind="props.to ? { to: props.to } : {}"
    >
      <Button
        v-bind="{ ...$attrs }"
        ref="buttonRef"
        :class="{
          [props.class || '']: true,
          'p-button-icon-only': onlyIcon,
        }"
        :loading="loading"
        :label="label"
        :disabled="loading || disabled"
        @click.prevent="handleClick"
      >
        <Icon
          v-if="(icon || loading) && iconPos !== 'right'"
          :size="iconSize"
          :style="{ minWidth: iconSize + 'px' }"
          :name="loading ? 'svg-spinners:180-ring' : icon || ''"
        />
        <span
          v-if="label"
          :class="`font-${props.fontWeight}`"
        >
          {{ label }}
        </span>
        <slot />
        <Icon
          v-if="iconPos === 'right'"
          :style="{ minWidth: iconSize + 'px' }"
          :size="iconSize"
          :name="loading ? 'svg-spinners:180-ring' : icon || ''"
        />
      </Button>
    </component>
  </div>
</template>

<script setup lang="ts">
import Button from 'primevue/button'
import type { ButtonProps } from 'primevue/button'
import { useRouter, type RouteLocationRaw } from 'vue-router'

export interface AppButtonProps extends /* @vue-ignore */ ButtonProps {
  test?: string
  to?: RouteLocationRaw
  class?: string
  loading?: boolean
  disabled?: boolean
  fontWeight?: 'normal' | 'medium' | 'semibold' | 'bold' | 'black'
  label?: string
  icon?: string
  iconSize?: number
  iconPos?: 'left' | 'right'
}

const props = withDefaults(defineProps<AppButtonProps>(), {
  fontWeight: 'medium',
  loading: false,
  disabled: false,
  label: '',
  iconSize: 16,
})

const buttonRef = ref<HTMLButtonElement | null>(null)
provide('popoverTarget', buttonRef)
const emit = defineEmits<{
  click: [event: Event]
}>()

const router = useRouter()

const onlyIcon = computed(() => {
  return props.icon && !props.label
})

const handleClick = (event: Event) => {
  emit('click', event)
  if (props.to) {
    void router.push(props.to)
  }
  return
}
</script>
