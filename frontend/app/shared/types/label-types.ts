export const EMPTY_DATA_LABEL = '—'

export type LabelConfig = {
  label: string
  icon: string
  color: 'primary' | 'secondary' | 'success' | 'info' | 'warn' | 'help' | 'danger' | 'contrast'
  unknown?: boolean
}

export const UNKNOWN_LABEL: LabelConfig = {
  label: 'Не удалось определить',
  icon: 'lucide:question-mark',
  color: 'secondary',
  unknown: true
}
