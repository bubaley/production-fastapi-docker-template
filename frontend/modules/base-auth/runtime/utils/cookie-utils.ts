import type { H3Event } from 'h3'

export const parseCookieValue = (cookieName: string, event: H3Event, responseCookies?: string[]): string | null => {
  if (responseCookies?.length) {
    for (const cookie of responseCookies) {
      const match = cookie.match(new RegExp(`${cookieName}=([^;]+)`))
      if (match) return match[1] || null
    }
  }
  return getCookie(event, cookieName) || null
}
