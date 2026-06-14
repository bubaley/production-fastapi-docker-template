export const useAppImageLightboxStore = defineStore('app-image-lightbox', () => {
  const sources = ref<string[]>([])
  const show = ref(false)
  const initialIndex = ref(0)

  const open = (values: string[], index = 0) => {
    sources.value = values
    initialIndex.value = index < 0 ? 0 : index
    show.value = true
  }

  const close = () => {
    show.value = false
  }

  return { sources, show, initialIndex, open, close }
})
