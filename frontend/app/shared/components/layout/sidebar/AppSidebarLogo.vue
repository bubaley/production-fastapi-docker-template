<template>
  <NuxtLink
    :to="{ name: 'home' }"
    class="flex max-w-full min-w-0 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-ring"
    :class="subtle ? 'h-[44px] w-full items-center justify-center px-2 md:h-9' : 'p-1'"
    :aria-label="`${name}: главная`"
  >
    <AppLogo
      :compact="!subtle"
      :subtle="subtle"
    />
  </NuxtLink>
</template>

<script setup lang="ts">
import AppLogo from '../header/AppLogo.vue'

defineProps<{
  /** The quiet variant above the account block in the sidebar footer: a centered row as tall as the account row. */
  subtle?: boolean
}>()

const { name } = useAppConfig()
</script>
