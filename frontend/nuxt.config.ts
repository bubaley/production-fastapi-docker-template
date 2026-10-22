import tailwindcss from '@tailwindcss/vite'

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
    }
  },
  modules: [
    '@nuxt/eslint',
    '@nuxt/icon',
    '@nuxt/fonts',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    '@nuxtjs/google-fonts',
    './modules/base-auth',
    'dayjs-nuxt',
  ],
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
    }
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
      'shared/ui/app/composables/**',
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
    storageKey: 'colorScheme',
  },
  googleFonts: {
    families: {
      Inter: '100..900',
    },
    display: 'swap'
  },
  vite: {
    plugins: [tailwindcss()],
  },
  typescript: {
    typeCheck: false,
  },
  css: ['~/assets/styles/tailwind.css', '~/assets/styles/global.scss', '~/assets/styles/variables.scss', '~/assets/styles/template.scss'],
  devServer: {
    port: 8080,
    host: 'localhost',
  },
})
