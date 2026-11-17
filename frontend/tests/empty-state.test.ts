import { describe, expect, it } from 'vite-plus/test'
import { mount } from '@vue/test-utils'
import { h } from 'vue'
import AppEmptyState from '../app/shared/ui/app/AppEmptyState.vue'

const render = (props: Record<string, unknown> = {}, actions?: string) =>
  mount(AppEmptyState, {
    props,
    slots: actions ? { actions: () => h('button', { type: 'button' }, actions) } : undefined,
  })

describe('AppEmptyState', () => {
  it('shows the Russian default copy in a dashed, centered frame', () => {
    const wrapper = render()
    const root = wrapper.get('[role="status"]')
    expect(wrapper.get('h3').text()).toBe('Здесь пока пусто')
    expect(root.classes()).toEqual(expect.arrayContaining(['border-dashed', 'items-center', 'text-center']))
  })

  it('drops the frame and centering for a plain start-aligned state', () => {
    const root = render({ title: 'Нет участников', bordered: false, align: 'start' }).get('[role="status"]')
    expect(root.classes()).not.toContain('border-dashed')
    expect(root.classes()).toEqual(expect.arrayContaining(['items-start', 'text-left']))
  })

  it('announces failures as alerts and renders the actions slot', () => {
    const wrapper = render({ title: 'Не удалось загрузить', tone: 'destructive' }, 'Повторить')
    expect(wrapper.get('[role="alert"]').text()).toContain('Не удалось загрузить')
    expect(wrapper.get('button').text()).toBe('Повторить')
  })

  it('renders the quiet variant as one muted regular-weight line without a heading or frame', () => {
    const wrapper = render({ variant: 'quiet', title: 'Никого не нашли', tone: 'muted' })
    const root = wrapper.get('[role="status"]')
    expect(root.classes()).not.toContain('border-dashed')
    expect(wrapper.find('h3').exists()).toBe(false)
    const text = wrapper.get('p')
    expect(text.text()).toBe('Никого не нашли')
    expect(text.classes()).toEqual(expect.arrayContaining(['text-sm', 'text-muted-foreground']))
    expect(text.classes()).not.toContain('font-semibold')
    expect(render({ variant: 'quiet', title: 'Ошибка', tone: 'destructive' }).find('[role="alert"]').exists()).toBe(
      true,
    )
  })

  it('lays out the inline variant as a row from sm', () => {
    const root = render({ variant: 'inline', align: 'center' }).get('[role="status"]')
    expect(root.classes()).toEqual(expect.arrayContaining(['sm:flex-row']))
    expect(root.classes()).not.toContain('text-center')
  })
})
