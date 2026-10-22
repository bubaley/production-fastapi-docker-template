<script setup lang="ts">
import { computed, type HTMLAttributes } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '~/shared/ui/shadcn/dialog'
import { useOverlayStack } from './useOverlayStack'

export type AppModalProps = {
  title?: string
  description?: string
  subtitle?: string
  width?: string
  closeLabel?: string
  closeable?: boolean
  contentClass?: HTMLAttributes['class']
  bodyClass?: HTMLAttributes['class']
  hideTitle?: boolean
  preventOutsideClose?: boolean
  escapeDisabled?: boolean
  autofocus?: boolean
}

const props = withDefaults(defineProps<AppModalProps>(), {
  width: '32rem',
  closeable: true,
  autofocus: true
})

const model = defineModel<boolean>({ default: false })
const { backdropStyle: overlayStyle, contentStyle: layerStyle, isTop } = useOverlayStack(model)
const contentStyle = computed(() => ({ '--app-modal-width': props.width, ...layerStyle.value }))

type InteractOutsideEvent = Event & { detail?: { originalEvent?: Event } }

const handleInteractOutside = (event: InteractOutsideEvent) => {
  const originalPath = event.detail?.originalEvent?.composedPath() ?? []
  const isDevToolsInteraction = originalPath.some(
    (target) => target instanceof Element && target.closest('#__vue-devtools-container__')
  )
  const isPortalledOverlayInteraction = originalPath.some(
    (target) =>
      target instanceof Element &&
      (target.closest('[data-reka-popper-content-wrapper]') ||
        target.closest('[data-sonner-toaster]') ||
        target.closest('.viewer-container'))
  )

  if (!isTop.value || props.preventOutsideClose || isDevToolsInteraction || isPortalledOverlayInteraction)
    event.preventDefault()
}
</script>

<template>
  <Dialog v-model:open="model">
    <DialogContent
      :show-close="closeable"
      :close-label="closeLabel"
      :style="contentStyle"
      :overlay-style="overlayStyle"
      :class="['max-w-[var(--app-modal-width)] border-border', contentClass]"
      @interact-outside="handleInteractOutside"
      @escape-key-down="escapeDisabled && $event.preventDefault()"
      @open-auto-focus="!autofocus && $event.preventDefault()"
    >
      <DialogTitle
        v-if="!title"
        class="sr-only"
      >
        Модальное окно
      </DialogTitle>
      <DialogDescription
        v-if="!description && !subtitle"
        class="sr-only"
      >
        Дополнительные сведения и действия.
      </DialogDescription>
      <DialogHeader
        v-if="title || description || subtitle"
        :class="hideTitle && 'sr-only'"
      >
        <div
          v-if="title || $slots['title-actions']"
          class="flex min-w-0 items-center gap-2"
          :class="$slots['title-actions'] && 'pr-6'"
        >
          <DialogTitle
            v-if="title"
            class="min-w-0 text-lg font-semibold text-foreground"
          >
            {{ title }}
          </DialogTitle>
          <div
            v-if="$slots['title-actions']"
            class="flex shrink-0 items-center gap-1"
          >
            <slot name="title-actions" />
          </div>
        </div>
        <DialogDescription
          v-if="description || subtitle"
          class="text-sm text-muted-foreground"
        >
          {{ description || subtitle }}
        </DialogDescription>
      </DialogHeader>

      <div :class="['min-w-0', bodyClass]">
        <slot />
      </div>

      <DialogFooter v-if="$slots.footer">
        <slot name="footer" />
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
