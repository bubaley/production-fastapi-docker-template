import { userTokenCodec } from '../models/userToken'

export const useUserTokenRepo = defineStore('userTokenRepo', () => {
  const config = getRepoConfig({
    resource: 'user-tokens',
    codec: userTokenCodec,
    parseResponse: (raw, action) => {
      const decoded = userTokenCodec.decode(raw)
      if (import.meta.client && action === 'create' && decoded.value) {
        try {
          const { notify } = useNotify()
          notify({
            severity: 'success',
            summary: 'Токен создан',
            detail: decoded.value,
            life: 120_000,
          })
        } catch {
          /* composable outside setup */
        }
      }
      return decoded
    },
  })
  const { state, actions } = createAppRepo(config)()

  return {
    ...state,
    ...actions,
  }
})
