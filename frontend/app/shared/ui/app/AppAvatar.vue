<template>
  <Avatar
    shape="circle"
    :size="size"
    :style="_style"
  >
    <Image
      v-if="src"
      :src="src"
    />
    <span
      v-else
      class="text-white font-semibold"
    >
      {{ name?.slice(0, 1) }}
    </span>
    <slot />
  </Avatar>
</template>

<script lang="ts" setup>
export type CAvatarSize = 'normal' | 'large' | 'xlarge' | 'small' | 'xsmall'
export interface CAvatarProps {
  color?: string | null
  name?: string | null
  src?: string | null
  size?: CAvatarSize
}

const props = withDefaults(defineProps<CAvatarProps>(), {
  size: 'normal',
})

const _style = computed(() => {
  const values = []
  if (props.src) values.push('background: transparent')
  else if (props.color) values.push(`background: ${props.color}`)
  if (props.size === 'small') values.push(`height: 24px; width: 24px`)
  if (props.size === 'xsmall') values.push(`height: 20px; width: 20px`)
  return values.join('; ')
})
</script>
