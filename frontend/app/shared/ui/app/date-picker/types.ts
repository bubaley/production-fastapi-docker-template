/** Calendar dates use YYYY-MM-DD; local date-times use YYYY-MM-DDTHH:mm.
 * Smart values retain their expression until explicitly resolved by the consumer. */
export type DatePickerRange = { start: string | null; end: string | null }
export type DatePickerTriggerBindings = {
  id?: string
  'aria-describedby'?: string
  'aria-invalid'?: boolean
  mode: 'single' | 'range'
  modelValue: string | null
  range: DatePickerRange
  value: string | null | DatePickerRange
  formattedValue: string
  open: boolean
  disabled: boolean
  readonly: boolean
}
export type DatePickerProps = {
  id?: string
  name?: string
  describedBy?: string
  hint?: string
  error?: string
  required?: boolean
  /** Allow independently cleared/open range boundaries. */
  allowPartial?: boolean
  mode?: 'single' | 'range'
  inline?: boolean
  /** Enables optional time selection in the same field. */
  time?: boolean
  /** Shared date-first input/display mask; model values remain ISO. */
  mask?: string
  /** Show an overlay clear button while a populated date input is hovered or focused. */
  clearable?: boolean
  applyMode?: 'manual' | 'auto' | 'close'
  /** Interval between suggested times, in minutes. Arbitrary minutes can still be typed. */
  timeStep?: number
  smart?: boolean
  navigation?: 'scroll' | 'paged'
  months?: 1 | 2
  locale?: 'ru' | 'en'
  label?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  min?: string
  max?: string
}

export type DatePickerEndpoint = 'start' | 'end'
