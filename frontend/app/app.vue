<template>
  <NuxtLayout><NuxtPage /></NuxtLayout>
  <AppToaster />
  <ClientOnly><AppImageLightbox /></ClientOnly>
</template>

<script setup lang="ts">
import AppImageLightbox from '~/shared/ui/app/AppImageLightbox.client.vue'
</script>
<style></style>
