<template>
  <component
    :is="to ? 'router-link' : 'div'"
    :type="to ? undefined : 'div'"
    :to="to"
    class="inline-flex items-center gap-1.5"
    :class="classes"
    @click="handleClick"
  >
    <Icon
      v-if="icon"
      :name="icon"
    />
    <span>{{ label }}<slot /></span>
  </component>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { useClipboard } from '@vueuse/core'

const props = withDefaults(
  defineProps<{
    label?: string
    weight?: WeightToken
    severity?: ColorToken
    icon?: string
    to?: string | RouteLocationRaw
    copied?: boolean
    value?: any
    underline?: boolean
  }>(),
  {
    severity: 'primary',
    underline: true,
  },
)

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()
const { copy } = useClipboard()
const { notify } = useNotify()

const classes = computed(() => {
  return [
    `font-${props.weight}`,
    `color-${props.severity}`,
    'cursor-pointer',
    'text-btn',
    { 'text-btn--no-underline': !props.underline },
  ]
})

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
    notify({ severity: 'success', summary: 'Cкопировано' })
  }
}
</script>

<style lang="scss" scoped>
@import '~/assets/styles/variables.scss';

.text-btn {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  text-align: inherit;
  cursor: pointer;
  user-select: none;
  transition: filter 0.2s;

  @each $name, $entry in $colors-map {
    $color: nth($entry, 1);

    &.color-#{$name} {
      color: $color;

      &:hover {
        filter: brightness(0.9);
      }
    }
  }

  &:not(.text-btn--no-underline):hover {
    text-decoration: underline;
  }
}
</style>
