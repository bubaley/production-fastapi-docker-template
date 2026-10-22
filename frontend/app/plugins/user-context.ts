import { useUserRepoReset } from '~/shared/composables/useRepo'

export default defineNuxtPlugin(() => {
  const { session } = useAuth()
  const resetRepos = useUserRepoReset()
  const setupStore = useSetupStore()
  const toast = useToast()
  watch(
    () => session.value?.id,
    (id, previousId) => {
      if (!previousId || id === previousId) return
      resetRepos()
      setupStore.reset()
      toast.dismiss()
    },
    { flush: 'sync' },
  )
})
