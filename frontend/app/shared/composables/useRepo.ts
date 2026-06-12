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
