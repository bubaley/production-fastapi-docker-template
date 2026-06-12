import { userCodec } from '../models/user'

export const useUserRepo = defineStore('userRepo', () => {
  const config = getRepoConfig({ resource: 'users', codec: userCodec })
  const { state, actions } = createAppRepo(config)()

  return {
    ...state,
    ...actions,
  }
})
