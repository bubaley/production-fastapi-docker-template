<script setup lang="ts">
import { Toaster, type ToasterProps } from 'vue-sonner'
import 'vue-sonner/style.css'
const props = defineProps<ToasterProps>()
</script>

<template>
  <Toaster v-bind="props" />
</template>
