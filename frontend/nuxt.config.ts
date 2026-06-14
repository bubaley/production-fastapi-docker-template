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
    '@primevue/nuxt-module',
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
    },
    {
      path: '~/shared/ui/template',
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
      'shared/toolkits/authentication/**',
      'shared/toolkits/repo/**',
      'shared/toolkits/repo/composables/**',
      'shared/toolkits/repo/types/**',
      // shared ui
      'shared/ui/app/composables/**',
      'shared/ui/template/types/**',
      'shared/ui/template/composables/**',
    ],
  },
  primevue: {
    importTheme: { from: '~/shared/ui/preset.ts' },
    options: {
      locale: {
        dayNames: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
        dayNamesShort: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
        dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
        monthNames: [
          'Январь',
          'Февраль',
          'Март',
          'Апрель',
          'Май',
          'Июнь',
          'Июль',
          'Август',
          'Сентябрь',
          'Октябрь',
          'Ноябрь',
          'Декабрь',
        ],
        monthNamesShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
        fileSizeTypes: ['B', 'KB', 'MB', 'GB', 'TB'],
        firstDayOfWeek: 1,
      },
    },
  },
  baseAuth: {
    apiPrefix: '/api/v1/auth',
    sessionRefresh: {
      beforeExpiry: 1300,
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
