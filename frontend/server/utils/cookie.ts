import type { H3Event } from 'h3'

export const getCookieValue = (name: string, event: H3Event, setCookies?: string[]) => {
  for (const cookie of setCookies || []) {
    const [keyValue] = cookie.split(';')
    if (keyValue) {
      const [key, value] = keyValue.split('=')
      if (key && key.trim() === name) {
        return value
      }
    }
  }
  return getCookie(event, name) || null
}
