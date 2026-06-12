<template>
  <div v-if="formattedDuration">{{ formattedDuration }}</div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    date: string
    hideZero?: boolean
    accuracy?: 'minutes' | 'seconds'
    onlyAccuracy?: boolean
  }>(),
  {
    hideZero: true,
    accuracy: 'minutes',
    onlyAccuracy: false,
  }
)

const { parseDate, now } = useDate()

const formattedDuration = computed(() => {
  if (!props.date) return ''

  const date = parseDate(props.date)
  if (!date) return ''

  const currentTime = now()
  const diffInSeconds = Math.abs(date.diff(currentTime, 'seconds'))
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  const diffInHours = Math.floor(diffInMinutes / 60)

  if (props.onlyAccuracy) {
    if (props.accuracy === 'seconds') {
      if (diffInSeconds === 0 && props.hideZero) return ''
      return `${diffInSeconds}с`
    }

    if (props.accuracy === 'minutes') {
      if (diffInMinutes === 0 && props.hideZero) return ''
      return `${diffInMinutes}м`
    }

    return ''
  }

  if (props.accuracy === 'seconds') {
    if (diffInSeconds < 60) {
      if (diffInSeconds === 0 && props.hideZero) return ''
      return `${diffInSeconds}с`
    }
  }

  if (diffInHours > 0) {
    const remainingMinutes = diffInMinutes % 60
    if (remainingMinutes === 0 && props.hideZero) {
      return `${diffInHours}ч`
    }
    return remainingMinutes > 0 ? `${diffInHours}ч ${remainingMinutes}м` : `${diffInHours}ч`
  }

  if (diffInMinutes > 0) {
    return `${diffInMinutes}м`
  }

  if (props.accuracy === 'seconds' && diffInSeconds > 0) {
    return `${diffInSeconds}с`
  }

  return ''
})
</script>
