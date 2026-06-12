export type AppDetailActionsSaveResult<T> = {
  item: T | undefined
  created: boolean
  success: boolean
}

export type AppDetailActionsDeleteResult<T> = {
  success: boolean
  item: T | undefined
}
