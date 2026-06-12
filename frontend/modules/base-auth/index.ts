import { defineNuxtModule, addServerHandler, addImports, createResolver, addPlugin, addRouteMiddleware } from 'nuxt/kit'
import type { BaseAuthModuleConfig, BaseAuthModuleOptions } from './types'
import { fileURLToPath } from 'url'


export default defineNuxtModule<BaseAuthModuleConfig>({
  meta: {
    name: '@nuxt/base-auth',
    configKey: 'baseAuth',
    alias: {
      '#base-auth': fileURLToPath(new URL('./', import.meta.url))
    },
    compatibility: {
      nuxt: '^4.0.0',
    },
  },
  defaults: {
    apiPrefix: '',
    nuxtApiPrefix: '/api/auth',
    endpoints: {
      login: {
        url: '/login',
        method: 'post',
      },
      logout: {
        url: '/logout',
        method: 'post',
      },
      refresh: {
        url: '/refresh',
        method: 'post',
      },
      getSession: {
        url: '/me',
        method: 'get',
      },
    },
    cookies: {
      accessToken: 'access_token',
      refreshToken: 'refresh_token',
    },
    sessionRefresh: {
      beforeExpiry: 300,
      interval: 0,
    },
    disableServerSideAuth: false,
    fetchSessionAfterLogin: true,
  } as BaseAuthModuleOptions,
  setup(options, nuxt) {
    // options is now fully typed as BaseAuthModuleOptions since defaults are applied
    const resolvedOptions = options as BaseAuthModuleOptions
    const resolver = createResolver(import.meta.url)
    nuxt.options.runtimeConfig = nuxt.options.runtimeConfig || {}
    nuxt.options.runtimeConfig.public.baseAuth = resolvedOptions

    // Add server API handlers
    addServerHandler({
      route: `${resolvedOptions.nuxtApiPrefix}/**`,
      handler: resolver.resolve('./runtime/server/api/auth/[...all]'),
      method: 'post',
    })

    // Add server utils
    nuxt.hook('nitro:config', async (nitroConfig) => {
      nitroConfig.alias = nitroConfig.alias || {}
      nitroConfig.alias['#base-auth'] = resolver.resolve('./')
    })

    // Add composables
    addImports({
      name: 'useAuth',
      from: resolver.resolve('./runtime/composables/useAuth'),
    })

    // Add plugin for $auth injection
    addPlugin(resolver.resolve('./runtime/plugins/auth-inject'))

    // Add global middleware
    addRouteMiddleware({
      name: 'auth',
      path: resolver.resolve('./runtime/middleware/auth.global.ts'),
      global: true,
    })

    // Add types
    nuxt.hook('prepare:types', ({ declarations }) => {
      declarations.push(`
        declare module '#auth/types' {
          const AuthModuleOptions: typeof import('${resolver.resolve('./types')}').AuthModuleOptions
          const AuthResponse: typeof import('${resolver.resolve('./types')}').AuthResponse
          const AuthState: typeof import('${resolver.resolve('./types')}').AuthState
          const TokenInfo: typeof import('${resolver.resolve('./types')}').TokenInfo
        }

        declare module '#base-auth' {
          interface Session extends import('${resolver.resolve('./types')}').Session {
            // This interface can be extended by consumers
          }
          export { Session }
          export * from '${resolver.resolve('./types')}'
        }

        declare module '#app' {
          interface NuxtApp {
            $auth: ReturnType<typeof import('${resolver.resolve('./runtime/composables/useAuth')}').useAuth>
          }
        }

        declare module 'vue' {
          interface ComponentCustomProperties {
            $auth: ReturnType<typeof import('${resolver.resolve('./runtime/composables/useAuth')}').useAuth>
          }
        }
      `)
    })
  },
})

export type { BaseAuthModuleOptions as AuthModuleOptions, AuthResponse, AuthState, TokenInfo } from './types'
