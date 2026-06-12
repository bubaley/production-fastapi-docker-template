<template></template>

<script setup lang="ts">
import 'viewerjs/dist/viewer.css'
import { api as viewerApi } from 'v-viewer'
import type Viewer from 'viewerjs'
import { useLightboxStore } from '~/shared/stores/lightboxStore'

const store = useLightboxStore()
let viewerInstance: Viewer | null = null

const handleKeyEvent = (e: KeyboardEvent) => {
  if (e.key === 'Escape' || e.key === 'Esc') {
    e.stopPropagation()
    viewerInstance?.hide()
  }
}

watch(
  () => store.show,
  (v) => {
    if (v) {
      document.addEventListener('keydown', handleKeyEvent, true)
      viewerInstance?.destroy()
      viewerInstance = viewerApi({
        images: store.sources,
        options: {
          inline: false,
          toolbar: false,
          navbar: true,
          title: false,
          initialViewIndex: store.initialIndex,
          hide: () => {
            store.close()
          },
        },
      })
    } else {
      document.removeEventListener('keydown', handleKeyEvent, true)
      viewerInstance?.destroy()
      viewerInstance = null
    }
  }
)
</script>
