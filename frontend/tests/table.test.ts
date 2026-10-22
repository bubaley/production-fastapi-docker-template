import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { h } from 'vue'
import AppTable from '../app/shared/ui/app/AppTable.vue'
import AppColumn from '../app/shared/ui/app/AppColumn.vue'

const items = [{ id: '1', name: 'Альфа', count: 2 }]
const createTable = (props = {}) => mount(AppTable, {
  props: { items, clickable: true, ...props },
  global: { stubs: { AppLoadingIndicator: { template: '<span role="status">Загрузка</span>' } } },
  slots: {
    default: () => [
      h(AppColumn, { field: 'name', header: 'Название' }),
      h(AppColumn, { header: 'Количество', format: (row: typeof items[number]) => `${row.count} шт.` }),
      h(AppColumn, { header: 'Действия' }, { body: ({ data }: { data: typeof items[number] }) => h('button', { type: 'button' }, `Изменить ${data.name}`) }),
    ],
  },
})

describe('AppTable declarative columns', () => {
  it('renders fields, formatted cells and scoped body slots', () => {
    const wrapper = createTable()
    expect(wrapper.findAll('th').map(node => node.text())).toEqual(['Название', 'Количество', 'Действия'])
    expect(wrapper.findAll('td').map(node => node.text())).toEqual(['Альфа', '2 шт.', 'Изменить Альфа'])
  })

  it('opens the row with Enter but isolates nested actions', async () => {
    const wrapper = createTable()
    await wrapper.get('button').trigger('click')
    await wrapper.get('button').trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('rowClick')).toBeUndefined()
    await wrapper.get('tbody tr').trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('rowClick')).toHaveLength(1)
    expect(wrapper.emitted('rowClick')?.[0]?.[0]).toMatchObject({ data: items[0], index: 0 })
  })

  it('keeps headers and correct colspan through empty, loading and error states', async () => {
    const wrapper = createTable({ items: [] })
    expect(wrapper.findAll('th')).toHaveLength(3)
    expect(wrapper.get('td').attributes('colspan')).toBe('3')
    expect(wrapper.text()).toContain('Данные отсутствуют')
    await wrapper.setProps({ loading: true })
    expect(wrapper.get('[role="status"]').text()).toBe('Загрузка')
    expect(wrapper.findAll('th')).toHaveLength(3)
    await wrapper.setProps({ loading: false, error: 'Ошибка загрузки' })
    expect(wrapper.get('[role="alert"]').text()).toBe('Ошибка загрузки')
    expect(wrapper.findAll('th')).toHaveLength(3)
  })

  it('never opens non-clickable rows', async () => {
    const wrapper = createTable({ clickable: false })
    await wrapper.get('tbody tr').trigger('click')
    expect(wrapper.emitted('rowClick')).toBeUndefined()
    expect(wrapper.get('tbody tr').attributes('tabindex')).toBeUndefined()
  })
})
