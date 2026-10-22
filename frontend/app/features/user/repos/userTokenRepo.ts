import { userTokenCodec } from '../models/userToken'

export const useUserTokenRepo = defineStore('userTokenRepo', () => {
  const config = getRepoConfig({
    resource: 'user-tokens',
    codec: userTokenCodec,
    parseResponse: (raw, action) => {
      const decoded = userTokenCodec.decode(raw)
      if (import.meta.client && action === 'create' && decoded.value) {
        useToast().default('Токен создан', { description: decoded.value, duration: 120_000 })
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
