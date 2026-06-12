import { organizationCodec, type Organization } from '../models/organization'

export const useOrganizationRepo = defineStore('organizationRepo', () => {
  const config = getRepoConfig({ resource: 'organizations', codec: organizationCodec })
  const { state, actions } = createAppRepo(config)()

  const organization = ref<Organization | null>(null)

  return {
    ...state,
    ...actions,
    organization,
  }
})
