import { describe, expect, it } from 'vite-plus/test'
import { mount } from '@vue/test-utils'
import AppPageView from '../app/shared/ui/app/AppPageView.vue'
import AppPage from '../app/shared/ui/app/AppPage.vue'

const global = {
  components: { AppPage },
  stubs: {
    AppTitle: { props: ['as'], template: '<component :is="as"><slot /></component>' },
    AppBackButton: true,
  },
}

describe('page composition', () => {
  it('scrolls the header and controls with the body by default and renders description once', () => {
    const wrapper = mount(AppPageView, {
      props: { title: 'Главная', description: 'Описание' },
      global,
      slots: {
        prefix: '<span>Иконка</span>',
        'title-append': '<span>Метка</span>',
        actions: '<button>Действие</button>',
        subheader: '<div>Под шапкой</div>',
        controls: '<div>Над содержимым</div>',
        default: '<div>Содержимое</div>',
        footer: '<div>Итоги</div>',
      },
    })
    expect(wrapper.findAll('h1')).toHaveLength(1)
    expect(wrapper.text().match(/Описание/g)).toHaveLength(1)
    expect(wrapper.get('footer').text()).toBe('Итоги')
    expect(wrapper.get('header').text()).toContain('Действие')
    // By default (`sticky="none"`) the header and the controls scroll with the content; only the footer is fixed.
    const regions = Array.from(wrapper.get('section').element.children)
    expect(regions.map((region) => region.getAttribute('data-slot') ?? region.tagName.toLowerCase())).toEqual([
      'page-body',
      'footer',
    ])
    const body = wrapper.get('[data-slot=page-body]')
    expect(body.get('[data-slot=page-header]').text()).toBe('ИконкаГлавнаяМеткаОписаниеДействиеПод шапкой')
    expect(body.get('[data-slot=page-controls]').text()).toBe('Над содержимым')
    expect(body.get('[data-slot=page-controls]').classes()).not.toContain('sticky')
    // No divider unless the page asks for one.
    expect(wrapper.find('.border-b.border-border').exists()).toBe(false)
  })

  it('pins the whole header area or only the controls bar on request', () => {
    const slots = { controls: '<div>Поиск</div>', default: '<div>Список</div>' }
    const header = mount(AppPageView, { props: { title: 'Список', sticky: 'header' }, global, slots })
    const [pinned, body] = Array.from(header.get('section').element.children)
    expect(pinned?.textContent).toContain('Список')
    expect(pinned?.textContent).toContain('Поиск')
    expect(body?.getAttribute('data-slot')).toBe('page-body')
    expect(body?.textContent?.trim()).toBe('Список')

    const controls = mount(AppPageView, { props: { title: 'Список', sticky: 'controls' }, global, slots })
    const bar = controls.get('[data-slot=page-body] [data-slot=page-controls]')
    expect(bar.classes()).toEqual(expect.arrayContaining(['sticky', 'top-0', 'bg-background']))
    expect(controls.get('[data-slot=page-body] [data-slot=page-header]').text()).toBe('Список')
  })

  it('adds the divider and limits every region to one column on request', () => {
    const wrapper = mount(AppPageView, {
      props: { title: 'Организация', divided: true, maxWidth: 'md', align: 'start' },
      global,
      slots: { controls: '<div>Поиск</div>', default: '<div>Форма</div>', footer: '<div>Итоги</div>' },
    })
    expect(wrapper.get('[data-slot=page-header]').classes()).toContain('border-b')
    const columns = wrapper.findAll('.max-w-\\(--page-width-md\\)')
    // Header, controls, body and footer share the column; `start` keeps it next to the navigation.
    expect(columns).toHaveLength(4)
    expect(columns.every((column) => !column.classes().includes('mx-auto'))).toBe(true)
  })

  it('supports custom titles, whole headers and the subtitle compatibility slot', () => {
    const title = mount(AppPageView, { global, slots: { title: 'Особый заголовок', subtitle: 'Старая панель' } })
    expect(title.get('h1').text()).toBe('Особый заголовок')
    expect(title.text()).toContain('Старая панель')
    const header = mount(AppPageView, {
      global,
      slots: { header: '<h1>Своя шапка</h1>', subtitle: 'Старая панель', subheader: 'Новая панель' },
    })
    expect(header.findAll('h1')).toHaveLength(1)
    expect(header.text()).toContain('Новая панель')
    expect(header.text()).not.toContain('Старая панель')
  })
})
