import type { BaseAuthModuleOptions } from '../../types'

export const getBaseAuthConfig = (): BaseAuthModuleOptions => {
  return useRuntimeConfig().public.baseAuth as BaseAuthModuleOptions
}
