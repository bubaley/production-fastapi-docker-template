<template>
  <div class="flex h-screen min-h-0 flex-col">
    <AppLayoutHeader hide-organization-picker />
    <AppPageLayout bordered>
      <slot />
    </AppPageLayout>
  </div>
</template>

<script setup lang="ts">
import AppLayoutHeader from '~/shared/components/layout/header/AppLayoutHeader.vue'
import AppPageLayout from '~/shared/components/layout/AppPageLayout.vue'
</script>
