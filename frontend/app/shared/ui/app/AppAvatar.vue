<template>
  <span
    :style="_style"
    class="app-avatar inline-flex items-center justify-center rounded-full bg-primary text-primary-foreground"
  >
    <img
      v-if="showImage"
      class="app-avatar__img"
      :src="src!"
      :alt="initial"
      @error="imageFailed = true"
    />
    <span
      v-else-if="!hasDefaultSlot"
      class="app-avatar__initial font-semibold text-white"
    >
      {{ initial }}
    </span>
    <slot />
  </span>
</template>

<script lang="ts" setup>
export type AppAvatarSize = 'normal' | 'large' | 'xlarge' | 'small' | 'xsmall'
export interface AppAvatarProps {
  color?: string | null
  name?: string | null
  src?: string | null
  size?: AppAvatarSize
}

const props = withDefaults(defineProps<AppAvatarProps>(), {
  size: 'normal',
})

const slots = useSlots()
const hasDefaultSlot = computed(() => Boolean(slots.default?.().length))
const imageFailed = ref(false)

watch(
  () => props.src,
  () => {
    imageFailed.value = false
  },
)

const AVATAR_SIZE: Record<AppAvatarSize, string> = {
  xsmall: '20px',
  small: '24px',
  normal: '2rem',
  large: '3rem',
  xlarge: '4rem',
}

const showImage = computed(() => Boolean(props.src) && !imageFailed.value)
const initial = computed(() => (props.name || '').trim().slice(0, 1).toUpperCase() || '?')

const _style = computed(() => {
  const size = AVATAR_SIZE[props.size]
  const values = [`width: ${size}`, `height: ${size}`, `min-width: ${size}`, `min-height: ${size}`]
  if (showImage.value) values.push('background: transparent')
  else if (props.color) values.push(`background: ${props.color}`)
  return values.join('; ')
})
</script>

<style lang="scss" scoped>
.app-avatar {
  overflow: hidden;
  flex-shrink: 0;
  aspect-ratio: 1 / 1;
}

.app-avatar__img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
