<script setup lang="ts">
definePageMeta({ path: '/home/ui' })
await navigateTo({ path: '/ui', query: useRoute().query }, { replace: true })
</script>
<template><div /></template>
