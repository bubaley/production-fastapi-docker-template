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
  it('keeps both fixed panels outside the scrolling body and renders description once', () => {
    const wrapper = mount(AppPageView, {
      props: { title: 'Главная', description: 'Описание' },
      global,
      slots: { prefix: '<span>Иконка</span>', 'title-append': '<span>Метка</span>', actions: '<button>Действие</button>', subheader: '<div>До разделителя</div>', controls: '<div>После разделителя</div>', default: '<div>Содержимое</div>', footer: '<div>Итоги</div>' },
    })
    expect(wrapper.findAll('h1')).toHaveLength(1)
    expect(wrapper.text().match(/Описание/g)).toHaveLength(1)
    expect(wrapper.get('main').text()).toBe('Содержимое')
    expect(wrapper.get('footer').text()).toBe('Итоги')
    expect(wrapper.get('header').text()).toContain('Действие')
    const regions = wrapper.get('section').element.children
    expect(Array.from(regions).map(region => region.textContent?.trim())).toEqual([
      'ИконкаГлавнаяМеткаОписаниеДействие', 'До разделителя', '', 'После разделителя', 'Содержимое', 'Итоги',
    ])
  })

  it('supports custom titles, whole headers and the subtitle compatibility slot', () => {
    const title = mount(AppPageView, { global, slots: { title: 'Особый заголовок', subtitle: 'Старая панель' } })
    expect(title.get('h1').text()).toBe('Особый заголовок')
    expect(title.text()).toContain('Старая панель')
    const header = mount(AppPageView, { global, slots: { header: '<h1>Своя шапка</h1>', subtitle: 'Старая панель', subheader: 'Новая панель' } })
    expect(header.findAll('h1')).toHaveLength(1)
    expect(header.text()).toContain('Новая панель')
    expect(header.text()).not.toContain('Старая панель')
  })
})
