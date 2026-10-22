import { afterEach, describe, expect, it } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h, ref } from 'vue'
import AppDrawer from '../app/shared/ui/app/AppDrawer.vue'
import AppModal from '../app/shared/ui/app/AppModal.vue'

let unmount: (() => void) | undefined
afterEach(() => { unmount?.(); document.body.innerHTML = '' })

describe('nested overlay layers', () => {
  it('opens a modal above its drawer and restores the drawer after closing', async () => {
    const open = ref(false)
    const wrapper = mount(defineComponent({
      setup: () => () => h(AppDrawer, { modelValue: true, overlay: true, title: 'Панель', 'data-drawer': '' }, {
        default: () => h(AppModal, { modelValue: open.value, title: 'Настройки' }, { default: () => h('input') }),
      }),
    }), { attachTo: document.body })
    unmount = () => wrapper.unmount()
    await flushPromises()
    const drawer = document.querySelector<HTMLElement>('[data-drawer][role="dialog"]')!
    const drawerLayer = Number(drawer.style.getPropertyValue('--app-overlay-z') || 1010)
    open.value = true
    await flushPromises()
    const modal = Array.from(document.querySelectorAll<HTMLElement>('[role="dialog"]')).find(element => element !== drawer)!
    expect(Number(modal.style.getPropertyValue('--app-overlay-z'))).toBeGreaterThan(drawerLayer)
    open.value = false
    await flushPromises()
    expect(drawer.getAttribute('data-state')).toBe('open')
    expect(drawer.style.getPropertyValue('--app-overlay-z')).toBe(String(drawerLayer))
  })
})
