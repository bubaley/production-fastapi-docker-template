import { useAuthClient } from '../../services/AuthClient'
import type { AuthResponse } from '../../../../types'

export default defineEventHandler(async (event) => {
  const authClient = useAuthClient()
  const action = getRouterParam(event, '_')

  const request = async (): Promise<AuthResponse | null> => {
    switch (action) {
      case 'login': {
        const credentials = await readBody(event)
        return await authClient.login(event, credentials)
      }
      case 'logout': {
        return await authClient.logout(event)
      }
      case 'refresh': {
        return await authClient.refresh(event)
      }
      case 'session':
      case 'me': {
        return await authClient.getSession(event)
      }
      case 'tokens': {
        return authClient.getTokens(event)
      }
      default: {
        return null
      }
    }
  }
  const response = await request()
  if (!response) {
    throw createError({
      statusCode: 404,
      statusMessage: `Not found`,
      data: `Auth action '${action}' not found`,
    })
  }
  return {
    ...response,
    cookies: undefined,
  }
})
