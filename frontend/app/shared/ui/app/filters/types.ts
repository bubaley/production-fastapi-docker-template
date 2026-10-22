import type { Component } from 'vue'
import type { SelectRepo } from '../select/types'
import type { AppLabelConfig } from '../types/label-types'
export type FilterValue = string | number | boolean | (string | number)[]
export type ViewFilters = Record<string, FilterValue>
export interface ViewFilterField {
  icon?: Component
  quick?: boolean
  field: string
  label: string
  kind: 'choice' | 'text' | 'number' | 'date' | 'datetime' | 'boolean'
  lookups: string[]
  items?: { id: string | number; name: string; appearance?: AppLabelConfig }[]
  repo?: SelectRepo<object> & { retrieve?(id: string | number): Promise<object | undefined> }
  query?: Record<string, unknown>
  itemLabel?: string | ((item: unknown) => string)
}
export interface ViewFilterSpec {
  fields: ViewFilterField[]
}


export interface ViewFixedField {
  field: string
  mode: 'single' | 'multiple' | 'optional'
  clearable?: boolean
  defaultValue?: FilterValue
  filterKeys?: string[]
}
