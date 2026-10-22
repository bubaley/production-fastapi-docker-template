import tailwindcss from '@tailwindcss/vite'
import { COLOR_MODE_COOKIE, paletteHeadScript } from './app/shared/lib/theme'

// FastAPI as seen from the Nuxt server: SSR requests and the dev proxy. The image sets http://127.0.0.1:8000.
const apiInternalUrl = process.env.NUXT_API_INTERNAL_URL || `http://localhost:${process.env.BACKEND_PORT || 9000}`
const clientOnly = { ssr: false }

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  experimental: {
    asyncContext: true,
  },
  // Server-only. Browsers always call the API on the page origin (`/api/v1`, `/ws`).
  runtimeConfig: {
    apiInternalUrl,
  },
  modules: ['@pinia/nuxt', '@pinia/colada-nuxt', '@nuxtjs/color-mode', './modules/dev-proxy'],
  devProxy: { target: apiInternalUrl },
  // Hybrid rendering: the signed-in app renders in the browser; public pages (`/`) render on the server.
  routeRules: {
    '/home': clientOnly,
    '/home/**': clientOnly,
    '/settings': clientOnly,
    '/settings/**': clientOnly,
    '/auth': clientOnly,
    '/ui': clientOnly,
  },
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
      'features/**/composables/**',
      // shared base
      'shared/composables/**',
      'shared/models/**',
      'shared/stores/**',
      'shared/utils/**',
      // shared ui
      'shared/ui/template/types/**',
      'shared/ui/template/composables/**',
    ],
  },
  colorMode: {
    preference: 'system',
    fallback: 'dark',
    dataValue: 'theme',
    storageKey: COLOR_MODE_COOKIE,
    // Cookie storage lets SSR render the right `data-theme` without a flash.
    storage: 'cookie',
  },
  nitro: {
    // Caddy serves the precompressed files (`file_server precompressed`).
    compressPublicAssets: { gzip: true, brotli: true },
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
