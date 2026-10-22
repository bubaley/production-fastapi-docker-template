import { createProxyServer } from 'httpxy'
import { defineNuxtModule, useLogger } from 'nuxt/kit'

type DevProxyOptions = { target: string }

/**
 * `nuxt dev` only: the browser talks to the API on the Nuxt origin, like behind Caddy in production, so the
 * HttpOnly session cookies and the CSRF Origin check behave the same. HTTP `/api/v1/**` goes through Nitro's
 * `devProxy`; websocket upgrades on `/ws/**` are taken over here, because Nitro's dev server hands every upgrade
 * to its own worker.
 */
export default defineNuxtModule<DevProxyOptions>({
  meta: { name: 'dev-proxy', configKey: 'devProxy' },
  setup(options, nuxt) {
    if (!nuxt.options.dev) return
    const target = options.target.replace(/\/+$/, '')
    const logger = useLogger('dev-proxy')

    // No changeOrigin: FastAPI sees the Nuxt host, which matches the browser's Origin.
    nuxt.options.nitro.devProxy = {
      ...nuxt.options.nitro.devProxy,
      '/api/v1': { target: `${target}/api/v1` },
    }

    const proxy = createProxyServer({ target, ws: true })
    proxy.on('error', (error) => logger.warn(`${target} is unreachable: ${error.message}`))
    nuxt.hook('listen', (server) => {
      const handlers = server.listeners('upgrade') as ((...args: unknown[]) => void)[]
      server.removeAllListeners('upgrade')
      server.on('upgrade', (req, socket, head) => {
        if (req.url?.startsWith('/ws/')) {
          proxy.ws(req, socket, { target }, head).catch(() => socket.destroy())
          return
        }
        for (const handler of handlers) handler.call(server, req, socket, head)
      })
    })
    logger.info(`/api/v1 and /ws -> ${target}`)
  },
})
