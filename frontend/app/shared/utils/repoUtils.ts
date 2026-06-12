import type { $Fetch } from 'ofetch'

const DEFAULT_PAGE_SIZE = 50

export type PaginationResponse = {
  meta?: {
    page: number
    page_size: number
    total: number
    pages: number
    has_next: boolean
  }
}

export type GetRepoConfigParams<T> = Omit<AppRepoConfig<T>, 'apiClient' | 'paginationCodec'> & {
  apiClient?: $Fetch
  repoName?: string
  paginationCodec?: AppCodec<AppPagination>
}

export type GetRepoConfigResult<T> = AppRepoConfig<T> & {
  repoName: string
}

export const paginationCodec = createCodec<AppPagination>({
  decode: (raw?: PaginationResponse) => {
    const page = raw?.meta?.page || 1
    let pages = raw?.meta?.pages || 0

    if (typeof raw?.meta?.has_next === 'boolean' && !pages) {
      pages = raw.meta.has_next ? page + 1 : page
    }


    return {
      page,
      size: raw?.meta?.page_size || DEFAULT_PAGE_SIZE,
      total: raw?.meta?.total || 0,
      pages,
      has_next: raw?.meta?.has_next ?? page < pages,
    }
  },
  encode: (v) => ({
    page: v.page,
    page_size: v.size,
  }),
})

export const getRepoConfig = <T>(config: GetRepoConfigParams<T>): GetRepoConfigResult<T> => {
  return {
    repoName: config.repoName || `${config.resource}Repo`,
    manyDataKey: 'data',
    paginationCodec: config.paginationCodec || paginationCodec,
    apiClient: config.apiClient || (useNuxtApp().$api as $Fetch),
    ...config,
  }
}
