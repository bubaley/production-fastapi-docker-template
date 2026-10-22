import { useWebSocket } from '@vueuse/core'
import type { MaybeRefOrGetter } from 'vue'

export interface WebSocketMessage {
  type: string
  data: unknown
}

export interface UseWebSocketOptions {
  onMessage?: (type: string, data: unknown) => void
  autoReconnect?: {
    retries?: number
    delay?: number
    onFailed?: () => void
  }
  immediate?: boolean
}

const resolveChannelValue = (channel: MaybeRefOrGetter<string | null>): string | null => {
  if (typeof channel === 'function') return channel()
  if (isRef(channel)) return channel.value
  return channel
}

// Same origin as the page: Caddy (production) and the dev proxy (`nuxt dev`) route `/ws/*` to FastAPI, and the
// browser sends the HttpOnly access cookie with the handshake — no token in the URL.
const resolveWsBaseUrl = (): string | undefined => {
  if (!import.meta.client) return undefined
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws`
}

export const useWebSocketService = (channel: MaybeRefOrGetter<string | null>, options: UseWebSocketOptions = {}) => {
  const wsBaseUrl = resolveWsBaseUrl()

  const wsUrl = computed(() => {
    const channelValue = resolveChannelValue(channel)
    if (!wsBaseUrl || !channelValue) return undefined
    return `${wsBaseUrl}/${channelValue.replace(/^\/+/, '')}`
  })

  const closedStatus = ref<'OPEN' | 'CONNECTING' | 'CLOSED'>('CLOSED')

  if (import.meta.server) {
    return {
      open: () => {},
      close: () => {},
      status: closedStatus,
    }
  }

  const { open, close, status } = useWebSocket(wsUrl, {
    immediate: false,
    autoConnect: false,
    autoClose: true,
    autoReconnect: options.autoReconnect ?? {
      delay: 1000,
      onFailed: () => {
        console.error('WebSocket connection failed')
      },
    },
    onMessage: (_ws: WebSocket, event: MessageEvent) => {
      try {
        const parsed = JSON.parse(event.data) as WebSocketMessage
        if (parsed.type && options.onMessage) {
          options.onMessage(parsed.type, parsed.data)
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    },
  })

  watch(
    wsUrl,
    (url) => {
      if (url) {
        open()
      } else {
        close()
      }
    },
    { immediate: options.immediate ?? true },
  )

  onBeforeUnmount(() => {
    close()
  })

  return {
    open,
    close,
    status,
  }
}
