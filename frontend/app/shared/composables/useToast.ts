import { toast as sonner } from 'vue-sonner'

export type ToastId = string | number
export type ToastConfig = {
  id?: ToastId
  description?: string
  duration?: number
  dismissible?: boolean
  closeButton?: boolean
  action?: { label: string; onClick: (event: MouseEvent) => void }
  cancel?: { label: string; onClick: (event: MouseEvent) => void }
}

// Keep vendor types and presentation policy out of feature consumers.
export const toast = {
  default: (message: string, config?: ToastConfig): ToastId => sonner(message, config),
  success: (message: string, config?: ToastConfig): ToastId => sonner.success(message, config),
  info: (message: string, config?: ToastConfig): ToastId => sonner.info(message, config),
  warning: (message: string, config?: ToastConfig): ToastId => sonner.warning(message, config),
  error: (message: string, config?: ToastConfig): ToastId => sonner.error(message, config),
  loading: (message: string, config?: ToastConfig): ToastId => sonner.loading(message, config),
  dismiss: (id?: ToastId): void => {
    sonner.dismiss(id)
  },
}

/** Also available outside setup (API interceptors and repositories). */
export function useToast() {
  return toast
}
