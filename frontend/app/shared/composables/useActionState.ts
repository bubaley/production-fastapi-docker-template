import { useDebounceFn } from '@vueuse/core'

export type AppStateNotification<T> = string | NotifyParams | ((data: T) => string | NotifyParams)

export interface AppStateParams<T> {
  errorNotification?: AppStateNotification<T>
  successNotification?: AppStateNotification<T>
  debounce?: number
}

export const useActionState = <T>(
  fn: (...args: any[]) => Promise<T> | T,
  params?: AppStateParams<T>,
) => {
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const data = ref<T | null>(null)
  const { notify: nottify } = useNotify()


  const _processNotification = (
    notification?: AppStateNotification<T>,
    severity?: 'success' | 'error',
  ) => {
    if (!notification) return
    let value: string | NotifyParams
    if (typeof notification === 'function') {
      value = notification(data.value as T)
    } else {
      value = notification
    }
    if (typeof value === 'string') {
      nottify({ severity: severity, summary: value })
    } else {
      nottify({ ...value, severity: severity })
    }
    return notification
  }

  const _execute = async (...args: any[]) => {
    try {
      data.value = await fn(...args)
      _processNotification(params?.successNotification, 'success')
      return data.value
    } catch (e) {
      error.value = e as Error
      _processNotification(params?.errorNotification, 'error')
      throw e
    } finally {
      loading.value = false
    }
  }

  const debouncedExecute = params?.debounce
    ? useDebounceFn((...args: any[]) => _execute(...args), params.debounce)
    : null

  const execute = (...args: any[]) => {
    loading.value = true
    error.value = null
    return debouncedExecute ? debouncedExecute(...args) : _execute(...args)
  }

  return { loading, error, data, execute }
}
