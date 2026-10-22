import type { Component } from 'vue'
import { Calendar, Hash, Type, ToggleLeft, Filter } from '@lucide/vue'
import type { ViewFilterField } from './types'
const kindIcons = { choice: Filter, text: Type, number: Hash, date: Calendar, datetime: Calendar, boolean: ToggleLeft }
export const filterIcon = (field: ViewFilterField): Component =>
  field.icon ?? kindIcons[field.kind]
const names: Record<string, string> = {
  range: 'Период',
  exact: 'Равно',
  in: 'Из',
  not_exact: 'Не равно',
  not_in: 'Не из',
  not_icontains: 'Не содержит',
  gt: 'Больше',
  lt: 'Меньше',
  gte: 'Не меньше',
  lte: 'Не больше',
  isnull: 'Не заполнено',
  icontains: 'Содержит'
}
const englishNames: Record<string, string> = {
  range: 'Range',
  exact: 'Equals',
  in: 'Any of',
  not_exact: 'Not equal',
  not_in: 'None of',
  not_icontains: 'Does not contain',
  gt: 'Greater than',
  lt: 'Less than',
  gte: 'At least',
  lte: 'At most',
  isnull: 'Is empty',
  icontains: 'Contains'
}
export const filterLookupLabel = (lookup: string, locale: 'ru' | 'en') =>
  (locale === 'en' ? englishNames : names)[lookup] || lookup
