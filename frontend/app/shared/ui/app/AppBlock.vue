<template>
  <div
    class="app-block"
    :class="_class"
    @click.capture="onClickCapture"
  >
    <Icon
      v-if="icon || loading"
      :name="loading ? 'svg-spinners:180-ring' : icon || ''"
      class="app-block-icon"
      :class="{ 'mr-2': hasDefaultSlot }"
    />
    <slot />
    <slot name="overlay" />
  </div>
</template>

<script lang="ts" setup>
import { Comment, computed, Fragment, Text, useSlots } from 'vue'

export type CBlockProps = {
  variant?: BlockVariantToken
  color?: ColorToken
  radius?: RadiusToken
  size?: SizeToken
  square?: boolean | 'unset'
  icon?: string
  button?: boolean
  loading?: boolean
  disabled?: boolean
  display?: 'row' | 'column' | 'inline-row'
  iconSize?: SizeToken
}

const { getRadiusBySize } = useDesignUtils()

const props = withDefaults(defineProps<CBlockProps>(), {
  variant: 'ghost',
  square: 'unset',
  display: 'inline-row',
})

const slots = useSlots()

function hasSlotContent(slot: ReturnType<typeof useSlots>['default']): boolean {
  if (!slot) return false
  return slot().some((vnode) => {
    if (vnode.type === Comment) return false
    if (vnode.type === Text) return !!vnode.children
    if (vnode.type === Fragment) return hasSlotContent(() => vnode.children as any)
    return true
  })
}

const hasDefaultSlot = computed(() => hasSlotContent(slots.default))

const isSquare = computed(() => {
  if (props.square !== 'unset') return props.square
  return !!(props.icon && !hasDefaultSlot.value)
})

function onClickCapture(e: MouseEvent) {
  if (props.loading || props.disabled) e.stopImmediatePropagation()
}

const _radius = computed<RadiusToken>(() => {
  if (!props.size) return 'sm'
  return props.radius || getRadiusBySize(props.size)
})

const _class = computed(() => {
  const classes: string[] = [`variant-${props.variant}`]
  if (props.color) classes.push(`color-${props.color}`)
  if (props.radius !== 'unset') classes.push(`radius-${props.radius || _radius.value}`)
  if (isSquare.value) classes.push('square')
  if (props.size) classes.push(`size-${props.size}`)
  if (props.button) classes.push('button')
  if (props.loading) classes.push('loading')
  if (props.disabled) classes.push('disabled')
  if (props.display) classes.push(`direction-${props.display}`)
  return classes
})
</script>

<style lang="scss" scoped>
@import '~/assets/styles/variables.scss';

.app-block {
  &.button {
    cursor: pointer;
    transition: background-color 0.2s;
  }

  &.direction-column {
    flex-direction: column;
    display: flex;
  }

  &.direction-row {
    display: flex;
    align-items: center;
  }

  &.direction-inline-row {
    display: inline-flex;
    align-items: center;
  }

  &.variant-outlined {
    border: 1px solid var(--border-base);
  }

  &.variant-ghost-outlined {
    border: 1px solid var(--border-base);
  }

  @each $name, $entry in $colors-map {
    $color: nth($entry, 1);
    $dark: nth($entry, 2);

    &.variant-ghost.color-#{$name} {
      background-color: color-mix(in srgb, $color 13%, transparent);
      color: $color;

      &.button:hover {
        background-color: color-mix(in srgb, $color 20%, transparent);
      }
    }

    &.variant-filled.color-#{$name} {
      background-color: color-mix(in srgb, $color 95%, transparent);
      color: if(sass($dark): #fff; else: #45464e);

      &.button:hover {
        background-color: color-mix(in srgb, $color 85%, black);
      }
    }

    &.variant-outlined.color-#{$name} {
      border: 1px solid color-mix(in srgb, $color 15%, transparent);
      color: $color;

      &.button:hover {
        background-color: color-mix(in srgb, $color 10%, transparent);
      }
    }

    &.variant-ghost-outlined.color-#{$name} {
      border: 1px solid color-mix(in srgb, $color 15%, transparent);
      background-color: color-mix(in srgb, $color 13%, transparent);
      color: $color;

      &.button:hover {
        background-color: color-mix(in srgb, $color 20%, transparent);
      }
    }
  }

  @each $size, $value in $radius-map {
    &.radius-#{$size} {
      border-radius: $value;
    }
  }

  &.radius-full {
    border-radius: 9999px;
  }

  @each $size, $height in $size-map {
    &.size-#{$size} {
      height: $height;

      .app-block-icon {
        font-size: $height / 2.5;
      }
    }
  }

  &.square {
    flex-shrink: 0;
    aspect-ratio: 1;
    width: auto;
    align-items: center;
    justify-content: center;
  }

  &.loading,
  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }

  &.loading {
    pointer-events: auto;
  }
}
</style>
