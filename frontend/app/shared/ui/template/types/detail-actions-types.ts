export type AppDetailActionsSaveResult<F, T = unknown> = {
  /** The form rebuilt from the saved record. */
  item: F | undefined
  /** The record the API returned. */
  saved?: T
  created: boolean
  success: boolean
}

export type AppDetailActionsDeleteResult<F> = {
  success: boolean
  item: F | undefined
}
