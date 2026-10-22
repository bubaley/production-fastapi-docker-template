const repoMap = {
  auth: useAuthRepo,
  organization: useOrganizationRepo,
  organizationUser: useOrganizationUserRepo,
  user: useUserRepo,
  userToken: useUserTokenRepo,
} as const

export type RepoKey = keyof typeof repoMap

export const useRepo = <K extends RepoKey>(key: K): ReturnType<(typeof repoMap)[K]> => {
  return repoMap[key]() as ReturnType<(typeof repoMap)[K]>
}

export const useUserRepoReset = () => {
  const repos = (['organization', 'organizationUser', 'user', 'userToken'] as const).map(key => useRepo(key))
  const organizationRepo = useRepo('organization')
  return () => {
    for (const repo of repos) repo.resetStore()
    organizationRepo.organization = null
  }
}
