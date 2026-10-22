import tailwindcss from '@tailwindcss/vite'
import { COLOR_MODE_COOKIE, paletteHeadScript } from './app/shared/lib/theme'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  experimental: {
    asyncContext: true,
  },
  runtimeConfig: {
    public: {
      baseUrl: undefined,
      apiPrefix: '/api/v1',
    },
  },
  modules: ['@pinia/nuxt', '@nuxtjs/color-mode', './modules/base-auth'],
  app: {
    head: {
      script: [{ innerHTML: paletteHeadScript, tagPosition: 'head' }],
    },
  },
  components: [
    {
      path: '~/shared/ui/app',
      pathPrefix: false,
      extensions: ['vue'],
    },
    {
      path: '~/shared/ui/template',
      pathPrefix: false,
      extensions: ['vue'],
    },
  ],
  imports: {
    dirs: [
      'composables/**',
      'features/**/repos/**',
      'features/**/models/**',
      'features/**/composables/**',
      // shared base
      'shared/composables/**',
      'shared/models/**',
      'shared/stores/**',
      'shared/utils/**',
      // shared toolkits
      'shared/toolkits/repo/**',
      'shared/toolkits/repo/composables/**',
      'shared/toolkits/repo/types/**',
      // shared ui
      'shared/ui/template/types/**',
      'shared/ui/template/composables/**',
    ],
  },
  baseAuth: {
    apiPrefix: '/api/v1/auth',
    sessionRefresh: {
      beforeExpiry: 60 * 30, // 30 minutes
      interval: 60 * 5, // 5 minutes
    },
  },
  colorMode: {
    preference: 'system',
    fallback: 'dark',
    dataValue: 'theme',
    storageKey: COLOR_MODE_COOKIE,
    // Cookie storage lets SSR render the right `data-theme` without a flash.
    storage: 'cookie',
  },
  vite: {
    plugins: [tailwindcss()],
  },
  typescript: {
    typeCheck: false,
  },
  css: ['~/assets/styles/tailwind.css'],
  devServer: {
    port: 9001,
    host: 'localhost',
  },
})
