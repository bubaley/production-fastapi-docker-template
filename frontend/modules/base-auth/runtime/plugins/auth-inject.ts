import { useAuth } from '../composables/useAuth'

export default defineNuxtPlugin(() => {
  const auth = useAuth()

  return {
    provide: {
      auth,
    },
  }
})
