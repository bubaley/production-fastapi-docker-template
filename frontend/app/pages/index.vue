<template><LandingView /></template>
<script setup lang="ts">
import LandingView from '~/features/landing/views/LandingView.vue'
import { ensureSession } from '~/shared/composables/useSession'

// The public page is for visitors: a signed-in user goes straight into the app.
definePageMeta({
  layout: false,
  auth: false,
  middleware: [
    async () => {
      if (await ensureSession()) return navigateTo({ name: 'home' }, { replace: true })
    },
  ],
})
</script>
