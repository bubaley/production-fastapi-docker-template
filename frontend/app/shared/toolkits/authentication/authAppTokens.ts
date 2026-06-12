// Simple type for API responses
export type BaseTokensRaw = {
  access_token: string | null
  refresh_token: string | null
} & Record<string, any>
