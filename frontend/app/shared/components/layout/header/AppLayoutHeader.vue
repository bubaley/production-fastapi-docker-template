<template>
  <header class="c-background z-10 flex min-h-[50px] items-center px-2">
    <AppLogo
      class="cursor-pointer"
      @click="navigateTo('/')"
    />
    <template v-if="!hideOrganizationPicker">
      <div class="mr-2 ml-4 opacity-30">/</div>
      <OrganizationPicker compact />
    </template>
    <div class="grow" />
    <AppHeaderProfileButton />
  </header>
</template>

<script setup lang="ts">
import OrganizationPicker from '~/features/organization/components/OrganizationPicker.vue'
import AppHeaderProfileButton from './AppHeaderProfileButton.vue'
import AppLogo from './AppLogo.vue'

defineProps<{
  hideOrganizationPicker?: boolean
}>()
</script>
