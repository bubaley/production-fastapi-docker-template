/** A `?redirect=` target limited to same-site paths: `/home`, never `//evil.example` or a full URL. */
export const safeRedirect = (value: unknown): string | null =>
  typeof value === 'string' && value.startsWith('/') && !value.startsWith('//') ? value : null
