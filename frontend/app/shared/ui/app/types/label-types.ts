import type { Component } from 'vue'
import { CircleQuestionMark } from '@lucide/vue'
import type { Tone } from '../tone'

export const EMPTY_DATA_LABEL = '—'

export type AppLabelConfig = {
  label: string
  icon: Component
  tone?: Tone
  unknown?: boolean
}

export const UNKNOWN_LABEL: AppLabelConfig = {
  label: 'Не удалось определить',
  icon: CircleQuestionMark,
  tone: 'muted',
  unknown: true,
}
