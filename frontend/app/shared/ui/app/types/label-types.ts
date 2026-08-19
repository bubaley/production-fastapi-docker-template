import type { ColorToken } from '../../template/types/template-ui-tokens'

export const EMPTY_DATA_LABEL = '—'

export type AppLabelConfig = {
  label: string
  icon: string
  color: ColorToken
  unknown?: boolean
}

export const UNKNOWN_LABEL: AppLabelConfig = {
  label: 'Не удалось определить',
  icon: 'lucide:circle-question-mark',
  color: 'secondary',
  unknown: true,
}
