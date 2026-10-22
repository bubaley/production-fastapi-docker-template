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

// The API origin (`NUXT_PUBLIC_BASE_URL`) serves `/ws`; without it the page origin does (Caddy proxies `/ws/*`).
const resolveWsBaseUrl = (): string | undefined => {
  const baseUrl = useRuntimeConfig().public.baseUrl as string | undefined
  const origin = baseUrl?.trim() || (import.meta.client ? window.location.origin : undefined)
  if (!origin) return undefined

  try {
    const url = new URL(origin)
    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${url.host}/ws`
  } catch {
    return undefined
  }
}

export const useWebSocketService = (
  channel: MaybeRefOrGetter<string | null>,
  options: UseWebSocketOptions = {},
) => {
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
