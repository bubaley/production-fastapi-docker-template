<script setup lang="ts">
import { Image, Pencil, Star } from '@lucide/vue'
import { useAppImageLightboxStore } from '~/shared/ui/app/stores/useAppImageLightboxStore'
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
const lightbox = useAppImageLightboxStore()
const renameValue = ref('Working project')
// Inline SVGs keep the demo offline.
const sampleImage = (label: string, color: string): string =>
  `data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600"><rect width="100%" height="100%" fill="${color}"/><text x="50%" y="50%" fill="#fff" font-family="sans-serif" font-size="48" text-anchor="middle" dominant-baseline="middle">${label}</text></svg>`,
  )}`
const images = [sampleImage('Image 1', '#2563eb'), sampleImage('Image 2', '#16a34a'), sampleImage('Image 3', '#c2410c')]
</script>

<template>
  <UiDemo
    title="Popover"
    code='AppMenu mode="popover" title content-class #default="{ close }"'
    description="A small free-form task next to its trigger. Call close() when it is done."
  >
    <AppMenu
      mode="popover"
      align="start"
      title="Rename project"
      content-class="w-72"
    >
      <template #trigger>
        <AppButton
          variant="outline"
          label="Rename"
          :icon="Pencil"
        />
      </template>
      <template #default="{ close }">
        <form
          class="flex flex-col gap-3 p-1.5"
          @submit.prevent="
            () => {
              toast.default(`Renamed to «${renameValue}»`)
              close()
            }
          "
        >
          <AppInput
            v-model="renameValue"
            label="Name"
          />
          <AppButton
            type="submit"
            label="Save"
            fluid
          />
        </form>
      </template>
    </AppMenu>
  </UiDemo>
  <UiDemo
    title="Tooltip"
    code="AppTooltip text #trigger"
    description="Explains an icon-only control on hover or keyboard focus. Not for essential information."
  >
    <AppTooltip text="Tooltips use the foreground color and open on hover or focus.">
      <template #trigger>
        <AppButton
          variant="outline"
          :icon="Star"
          aria-label="Favourite"
        />
      </template>
    </AppTooltip>
  </UiDemo>
  <UiDemo
    title="Image lightbox"
    code="useAppImageLightboxStore().open(images, index)"
    description="Full-screen preview of a set of images, mounted once in app.vue."
  >
    <AppButton
      variant="outline"
      label="Open lightbox"
      :icon="Image"
      @click="lightbox.open(images, 0)"
    />
  </UiDemo>
</template>
