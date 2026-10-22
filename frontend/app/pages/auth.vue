<template><AuthView /></template>
<script setup lang="ts">
import AuthView from '~/features/auth/views/AuthView.vue'
definePageMeta({ layout: 'auth', auth: 'guest' })
</script>
