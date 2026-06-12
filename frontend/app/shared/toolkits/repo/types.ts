import type { $Fetch } from 'ofetch'

export type LoadingState = {
  create: boolean
  update: boolean
  delete: boolean
  list: boolean
  retrieve: boolean
  action: boolean
}

// PaginationState type replaced with AppPagination class

export type SINGLE_ACTION = 'retrieve' | 'create' | 'update' | 'delete'
export type MANY_ACTION = 'list'

export type AppPaginatedResponse<T = unknown> = {
  [key: string]: T[] | unknown
}

export type AppCodec<T> = {
  decode: (v: any) => T
  encode: (v: T) => any
}

export type AppRepoConfig<T> = {
  resource: string
  apiClient: $Fetch
  // codec
  codec: AppCodec<T>
  paginationCodec: AppCodec<AppPagination>
  // response
  parseResponse?: (v: any, action: SINGLE_ACTION) => T
  parseManyResponse?: (v: any, action: MANY_ACTION) => { items: T[]; pagination: AppPagination }

  manyDataKey?: string
}

export type RepoListConfig = {
  storeInRepo?: boolean
  mode?: 'replace' | 'append' // default is replace
  pagination?: AppPagination
}

export type RepoException = {
  status_code?: number
  message?: string
}

export type RepoOnError = (error: RepoException) => void

export type AppRepo<T extends AppModel> = {
  item: T | null
  items: T[]
  loading: LoadingState
  pagination: AppPagination
  isLoading: boolean

  resetStore: () => void
  resetPagination: () => void

  list: (
    params?: Record<string, unknown>,
    config?: RepoListConfig,
    onError?: RepoOnError,
  ) => Promise<{ items: T[]; pagination: AppPagination } | undefined>
  retrieve: (id: string | number, params?: Record<string, unknown>, onError?: RepoOnError) => Promise<T | undefined>
  create: (object: T, onError?: RepoOnError) => Promise<T | undefined>
  update: (object: T, onError?: RepoOnError) => Promise<T | undefined>
  delete: (object: T, onError?: RepoOnError) => Promise<any | undefined>
  send: (...args: Parameters<AppApi['send']>) => Promise<unknown>
  encode: (object: T) => any
  decode: (object: any) => T
}

export type AppRepoStore<T extends AppModel> = Pick<
  AppRepo<T>,
  | 'item'
  | 'items'
  | 'pagination'
  | 'loading'
  | 'isLoading'
  | 'resetStore'
  | 'list'
  | 'retrieve'
  | 'create'
  | 'update'
  | 'delete'
  | 'send'
>
