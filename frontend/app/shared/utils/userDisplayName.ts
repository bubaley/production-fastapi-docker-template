type NamedUser = { first_name?: string | null; last_name?: string | null; email?: string | null }

/** «Имя Фамилия», else the email; empty for a missing user. */
export const userDisplayName = (user: NamedUser | null | undefined): string =>
  user ? `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim() || user.email || '' : ''
