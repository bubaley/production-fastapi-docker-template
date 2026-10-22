<template>
  <NuxtLayout><NuxtPage /></NuxtLayout>
  <AppToaster />
  <AppImageLightbox />
</template>

<script setup lang="ts">
// Self-hosted Inter (variable); the font stack lives in assets/styles/theme.css.
import '@fontsource-variable/inter'

const { palette } = useTheme()
useHead({ htmlAttrs: { 'data-palette': palette } })
</script>
