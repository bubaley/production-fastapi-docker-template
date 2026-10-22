import type { Component } from 'vue'
import type { AppControlSize, AppFieldVariant } from '../types/control'

export type SelectValue = string | number
export type SelectAccessor<T, V> = string | ((item: T) => V)
export type SelectModel<T, V, Multiple extends boolean, EmitValue extends boolean> = Multiple extends true
  ? EmitValue extends true
    ? V[]
    : T[]
  : EmitValue extends true
    ? V | null
    : T | null

/** Selection owns pagination and never mutates repository list state. */
export interface SelectRepo<T> {
  revision?: number
  list(
    params?: Record<string, unknown>,
    config?: import('~/shared/toolkits/repo/types').RepoListConfig,
  ): Promise<{ items: T[]; pagination: import('~/shared/toolkits/repo/appPagination').AppPagination } | undefined>
}
export interface SelectProps<T> {
  options?: T[]
  optionValue?: SelectAccessor<T, SelectValue>
  optionLabel?: SelectAccessor<T, string>
  extraParams?: Record<string, unknown>
  searchParam?: string
  filter?: boolean
  onlyClientSearch?: boolean
  filterFields?: string[]
  autoLoad?: boolean
  showClear?: boolean
  items?: T[]
  selectedItems?: T[]
  itemValue?: SelectAccessor<T, SelectValue>
  itemLabel?: SelectAccessor<T, string>
  itemDisabled?: SelectAccessor<T, boolean>
  repo?: SelectRepo<T>
  query?: Record<string, unknown>
  debounce?: number
  pageSize?: number
  multiple?: boolean
  emitValue?: boolean
  disabled?: boolean
}

export interface AppSelectProps<T> extends SelectProps<T> {
  id?: string
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  required?: boolean
  clearable?: boolean
  /** Reserve trailing space for an always-visible clear button. Default: overlay on hover/focus. */
  clearInline?: boolean
  icon?: Component
  name?: string
  variant?: AppFieldVariant
  /** Hide the disclosure icon. Inline selects hide it unless this is explicitly false. */
  hideDropdownIcon?: boolean
  locale?: 'ru' | 'en'
  ariaLabel?: string
  size?: AppControlSize
}
