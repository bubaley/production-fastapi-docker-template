<template>
  <Icon
    class="app-icon"
    :class="{
      'app-icon--gradient': Boolean(gradientSeverity),
      [`color-${color}`]: color,
    }"
    :name="loading ? 'svg-spinners:180-ring' : icon"
    :size="size"
    mode="css"
    :style="{
      minWidth: `${size}px`,
      '--app-icon-gradient': gradientImage,
    }"
  />
</template>

<script setup lang="ts">
import { appIconLinearGradient, type AppIconGradientSeverity } from '~/shared/ui/app/utils/iconGradients'

export type { AppIconGradientSeverity }

const props = withDefaults(
  defineProps<{
    icon: string
    size?: number
    loading?: boolean
    color?: ColorToken
    gradientSeverity?: AppIconGradientSeverity
  }>(),
  {
    size: 20,
    loading: false,
  },
)

const gradientImage = computed(() =>
  props.gradientSeverity ? appIconLinearGradient(props.gradientSeverity) : undefined,
)
</script>

<style lang="scss" scoped>
@import '~/assets/styles/variables.scss';

.app-icon {
  @each $name, $entry in $colors-map {
    $color: nth($entry, 1);

    &.color-#{$name} {
      color: $color;
    }
  }
}

.app-icon--gradient {
  background-color: transparent !important;
  background-image: var(--app-icon-gradient) !important;
}
</style>
