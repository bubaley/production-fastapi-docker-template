<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from '@lucide/vue'
import { Dialog, DialogContent, DialogDescription, DialogTitle } from '~/shared/ui/shadcn/dialog'
import { useAppImageLightboxStore } from './stores/useAppImageLightboxStore'
import { useOverlayStack } from './useOverlayStack'

// Mounted once in app.vue. Open it from anywhere: `useAppImageLightboxStore().open(urls, index)`.
const store = useAppImageLightboxStore()
const open = computed({
  get: () => store.show,
  set: (value: boolean) => {
    if (!value) store.close()
  },
})
const { backdropStyle, contentStyle } = useOverlayStack(open)
const count = computed(() => store.sources.length)
const current = computed(() => store.sources[store.initialIndex])
const step = (delta: number) => {
  if (count.value > 1) store.initialIndex = (store.initialIndex + delta + count.value) % count.value
}
const onKeydown = (event: KeyboardEvent) => {
  if (event.key === 'ArrowLeft') step(-1)
  if (event.key === 'ArrowRight') step(1)
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent
      :style="contentStyle"
      :overlay-style="backdropStyle"
      overlay-class="bg-black/80"
      class="flex max-h-[calc(100dvh-2rem)] w-auto max-w-[calc(100vw-2rem)] items-center justify-center border-0 bg-transparent p-0 shadow-none sm:max-w-[calc(100vw-4rem)]"
      close-label="Закрыть просмотр"
      @keydown="onKeydown"
    >
      <DialogTitle class="sr-only">Просмотр изображения</DialogTitle>
      <DialogDescription class="sr-only">
        Изображение {{ store.initialIndex + 1 }} из {{ count }}. Стрелки влево и вправо листают изображения.
      </DialogDescription>
      <img
        v-if="current"
        :src="current"
        :alt="`Изображение ${store.initialIndex + 1} из ${count}`"
        class="max-h-[calc(100dvh-4rem)] max-w-full rounded-lg object-contain"
      />
      <template v-if="count > 1">
        <AppButton
          :icon="ChevronLeft"
          variant="secondary"
          size="icon-lg"
          aria-label="Предыдущее изображение"
          class="absolute top-1/2 left-2 -translate-y-1/2 rounded-full"
          @click="step(-1)"
        />
        <AppButton
          :icon="ChevronRight"
          variant="secondary"
          size="icon-lg"
          aria-label="Следующее изображение"
          class="absolute top-1/2 right-2 -translate-y-1/2 rounded-full"
          @click="step(1)"
        />
        <span
          class="absolute bottom-2 left-1/2 -translate-x-1/2 rounded-full bg-background/80 px-2 py-0.5 text-xs text-foreground tabular-nums"
          aria-hidden="true"
          >{{ store.initialIndex + 1 }} / {{ count }}</span
        >
      </template>
    </DialogContent>
  </Dialog>
</template>
