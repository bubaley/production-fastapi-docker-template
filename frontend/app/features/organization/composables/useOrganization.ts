export const useOrganization = () => {
  const organizationRepo = useRepo('organization')
  const {session} = useAuth()

  const setDefaultOrganization = async () => {
    if (!organizationRepo.items.length) return
    organizationRepo.organization = organizationRepo.items.find(v => v.id === session.value?.organization_id) || organizationRepo.items[0] || null
    return organizationRepo.organization
  }

  const initOrganizations = async () => {
    await organizationRepo.list()
    return await setDefaultOrganization()
  }

  const organizationId = computed(() => organizationRepo.organization?.id || null)
  const organizationKey = computed(() => organizationRepo.organization?.key || null)


  return { organizationRepo, setDefaultOrganization, initOrganizations, organizationId, organizationKey }
}
