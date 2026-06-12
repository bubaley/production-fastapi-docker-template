<template>
  <div class="column gap-xs">
    <div
      class="title"
      :class="_class"
    >
      {{ title }}
      <slot />
    </div>
    <div
      v-if="subtitle"
      class="fg-secondary"
    >
      {{ subtitle }}
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: TitleSizeToken
    weight?: WeightToken
    title?: string
    subtitle?: string
  }>(),
  {
    size: 'xl',
  },
)

const defaultWeightBySize: Record<TitleSizeToken, WeightToken> = {
  sm: 'medium',
  md: 'semibold',
  lg: 'bold',
  xl: 'bold',
}

const _class = computed(() => {
  const classes: string[] = []
  if (props.size) classes.push(`size-${props.size}`)
  const weight = props.weight ?? (props.size ? defaultWeightBySize[props.size] : undefined)
  if (weight) classes.push(`weight-${weight}`)
  return classes
})
</script>

<style lang="scss" scoped>
@import '~/assets/styles/variables.scss';

.title {
  @each $size, $value in $title-size-map {
    &.size-#{$size} {
      font-size: $value;
    }
  }

  @each $name, $value in $weight-map {
    &.weight-#{$name} {
      font-weight: $value;
    }
  }
}
</style>
