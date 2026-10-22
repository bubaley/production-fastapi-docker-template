import { defineConfig } from '@hey-api/openapi-ts'

// `pnpm gen:api` writes the typed client for `openapi.json` (`make openapi`); `pnpm gen:api:check` regenerates it
// into GEN_API_OUT and fails when the committed output is stale.
export default defineConfig({
  input: './openapi.json',
  output: {
    path: process.env.GEN_API_OUT ?? './app/shared/api/generated',
    postProcess: [{ command: 'vp', args: ['fmt', '{{path}}'] }],
  },
  plugins: [
    '@hey-api/typescript',
    '@hey-api/sdk',
    // Operation paths already start with `/api/v1`; the base URL comes from the Nuxt plugin (`plugins/api.ts`).
    { name: '@hey-api/client-fetch', baseUrl: false },
  ],
})
