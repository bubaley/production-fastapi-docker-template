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

export function useWebSocketService(channel: MaybeRefOrGetter<string | null>, options: UseWebSocketOptions = {}) {
  const config = useRuntimeConfig()
  const baseUrl = config.public.wsURL as string | undefined

  const wsUrl = computed(() => {
    let channelValue: string | null
    if (typeof channel === 'function') {
      channelValue = channel()
    } else if (isRef(channel)) {
      channelValue = channel.value
    } else {
      channelValue = channel
    }
    if (!baseUrl || !channelValue) return ''
    return `${baseUrl}/${channelValue}`
  })

  const { open, close, status } = useWebSocket(wsUrl, {
    immediate: options.immediate ?? true,
    autoReconnect: options.autoReconnect ?? {
      delay: 1000,
      onFailed() {
        console.error('WebSocket connection failed')
      },
    },
    onMessage(_ws: WebSocket, event: MessageEvent) {
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
    () => wsUrl.value,
    (url) => {
      if (url) {
        open()
      } else {
        close()
      }
    },
    { immediate: true }
  )

  return {
    open,
    close,
    status,
  }
}
