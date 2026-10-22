import { describe, expect, it } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import AppFilterToolbar from '../app/shared/ui/app/filters/AppFilterToolbar.vue'
import type { ViewFilterSpec } from '../app/shared/ui/app/filters/types'
const spec: ViewFilterSpec = { fields: [
  { field: 'status', label: 'Статус', kind: 'choice', lookups: ['exact', 'in'] },
  { field: 'name', label: 'Название', kind: 'text', lookups: ['icontains'] },
] }
describe('filter toolbar integration', () => {
  it('uses inline conditions and excludes keys represented by fixed controls', () => {
    const wrapper = shallowMount(AppFilterToolbar, { props: { spec, modelValue: {}, fixedFields: [{ field: 'status', mode: 'multiple' }] } })
    const editor = wrapper.findComponent({ name: 'AppFilters' })
    expect(editor.props('inline')).toBe(true)
    expect(editor.props('excludedKeys')).toEqual(['status__in'])
    editor.vm.$emit('update:modelValue', { name__icontains: 'Проект' })
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([{ name__icontains: 'Проект' }])
  })
  it('keeps fixed controls independent of the available-filter menu', () => {
    const wrapper = shallowMount(AppFilterToolbar, { props: { spec, modelValue: {}, availableFields: ['name'], fixedFields: [{ field: 'status', mode: 'single' }] } })
    expect(wrapper.findComponent({ name: 'ViewFixedFilter' }).props('field').field).toBe('status')
    expect(wrapper.findComponent({ name: 'AppFilters' }).props('spec').fields.map((field: { field: string }) => field.field)).toEqual(['name'])
  })

  it('does not overwrite restored filters with fixed defaults', () => {
    const wrapper = shallowMount(AppFilterToolbar, { props: { spec, modelValue: { status__in: ['done'] }, fixedFields: [{ field: 'status', mode: 'single', defaultValue: 'active' }] } })
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })
  it('initializes fixed defaults and hides unavailable fields', () => {
    const wrapper = shallowMount(AppFilterToolbar, { props: { spec, modelValue: {}, hiddenFields: ['name'], fixedFields: [{ field: 'status', mode: 'single', defaultValue: 'active' }] } })
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([{ status: 'active' }])
    expect(wrapper.findComponent({ name: 'AppFilters' }).props('spec').fields.map((field: {field: string}) => field.field)).toEqual(['status'])
  })
})
