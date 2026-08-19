import { userCodec } from '../models/user'

export const useUserRepo = defineStore('userRepo', () => {
  const config = getRepoConfig({ resource: 'users', codec: userCodec })
  const { state, actions } = createAppRepo(config)()

  const changePassword = (
    id: string,
    data: { current_password?: string; new_password: string },
  ) =>
    actions.send({
      method: 'post',
      id,
      action: 'change-password',
      data,
    })

  return {
    ...state,
    ...actions,
    changePassword,
  }
})
