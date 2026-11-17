<template>
  <NuxtLoadingIndicator
    color="var(--primary)"
    :height="2"
    :throttle="150"
  />
  <NuxtLayout><NuxtPage /></NuxtLayout>
  <AppToaster />
  <AppImageLightbox />
</template>

<script setup lang="ts">
// Self-hosted Inter (variable); the font stack lives in assets/styles/theme.css.
import '@fontsource-variable/inter'

const { palette } = useTheme()
const { name } = useAppConfig()
// Browser tab: «Page · Product»; a page without its own title shows the product name.
useHead({
  htmlAttrs: { 'data-palette': palette },
  titleTemplate: (title) => (title && title !== name ? `${title} · ${name}` : name),
})
</script>
