import { ref } from 'vue'
import type { ToastConfig } from './useToast'

export type ActionNotification = { message: string } & ToastConfig
export type AppStateNotification<T> = string | ActionNotification | ((data: T) => string | ActionNotification)
export interface AppStateParams<T> {
  errorNotification?: AppStateNotification<T>
  successNotification?: AppStateNotification<T>
  debounce?: number
}

export const useActionState = <T>(fn: (...args: any[]) => Promise<T> | T, params?: AppStateParams<T>) => {
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const data = ref<T | null>(null)
  const toast = useToast()
  let pending: Promise<T> | undefined
  let timer: ReturnType<typeof setTimeout> | undefined
  let started = false
  let latestArgs: any[] = []
  let resolvePending: (value: T) => void
  let rejectPending: (reason: unknown) => void
  const notify = (notification: AppStateNotification<T> | undefined, kind: 'default' | 'error') => {
    if (!notification) return
    const value = typeof notification === 'function' ? notification(data.value as T) : notification
    if (typeof value === 'string') toast[kind](value)
    else {
      const { message, ...config } = value
      toast[kind](message, config)
    }
  }
  const run = async () => {
    started = true
    try {
      const value = await fn(...latestArgs)
      data.value = value
      notify(params?.successNotification, 'default')
      resolvePending(value)
    } catch (reason) {
      error.value = reason instanceof Error ? reason : new Error(String(reason))
      notify(params?.errorNotification, 'error')
      rejectPending(reason)
    } finally {
      loading.value = false
      started = false
      pending = undefined
    }
  }
  const schedule = () => {
    clearTimeout(timer)
    if (params?.debounce) timer = setTimeout(() => { void run() }, params.debounce)
    else void run()
  }
  const execute = (...args: any[]) => {
    if (pending) {
      if (!started) {
        latestArgs = args
        schedule()
      }
      return pending
    }
    latestArgs = args
    loading.value = true
    error.value = null
    const promise = new Promise<T>((resolve, reject) => {
      resolvePending = resolve
      rejectPending = reject
    })
    pending = promise
    schedule()
    return promise
  }
  return { loading, error, data, execute }
}
