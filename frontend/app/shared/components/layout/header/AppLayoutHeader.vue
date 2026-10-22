<template>
  <header class="z-10 flex min-h-[50px] items-center bg-background px-2">
    <AppLogo
      class="cursor-pointer"
      @click="navigateTo('/')"
    />
    <!-- Context region (e.g. the organization picker) is filled by the layout, which may import features. -->
    <template v-if="$slots.context">
      <div class="mr-2 ml-4 opacity-30">/</div>
      <slot name="context" />
    </template>
    <div class="grow" />
    <AppHeaderProfileButton />
  </header>
</template>

<script setup lang="ts">
import AppHeaderProfileButton from './AppHeaderProfileButton.vue'
import AppLogo from './AppLogo.vue'
</script>
