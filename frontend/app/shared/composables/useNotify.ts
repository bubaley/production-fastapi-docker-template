export interface NotifyParams {
  severity?: 'success' | 'info' | 'warn' | 'error' | 'secondary' | 'contrast'
  summary?: string
  detail?: string
  life?: number
}

const useNotify = () => {
  const toast = useToast()
  const notify = ({ severity = 'success', summary, detail, life = 1500 }: NotifyParams) => {
    toast.add({ severity: severity, summary: summary, detail: detail, life: life })
  }
  return { toast, notify, remove: toast.remove }
}

export default useNotify
