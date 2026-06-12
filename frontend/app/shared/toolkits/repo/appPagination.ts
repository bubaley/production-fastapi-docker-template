export const DEFAULT_PAGE_SIZE = 50

type AppPaginationRaw = DeepPartial<AppPagination>

export interface AppPagination {
  page: number
  size: number
  total: number
  pages: number
  has_next: boolean
}

export const paginationFromServer = (raw?: AppPaginationRaw): AppPagination => {
  const page = raw?.page || 1
  const pages = raw?.pages || 0
  return {
    page,
    size: raw?.size || DEFAULT_PAGE_SIZE,
    total: raw?.total || 0,
    pages,
    has_next: raw?.has_next ?? page < pages,
  }
}

export const paginationToServer = (data: AppPagination): any => {
  return {
    page: data.page,
    size: data.size,
  }
}

export const appPaginationCodec = createCodec<AppPagination>({
  decode: paginationFromServer,
  encode: paginationToServer,
})
