import { organizationUserCodec } from '../models/organizationUser'

export const useOrganizationUserRepo = defineStore('organizationUserRepo', () => {
  const config = getRepoConfig({ resource: 'organization-users', codec: organizationUserCodec })
  const { state, actions } = createAppRepo(config)()

  return {
    ...state,
    ...actions,
  }
})
