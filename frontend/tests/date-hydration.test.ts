import { afterEach, expect, it, vi } from 'vitest'
import { createSSRApp, h, nextTick, ref } from 'vue'
import { renderToString } from 'vue/server-renderer'
import AppDateRangeLabel from '../app/shared/ui/app/AppDateRangeLabel.vue'
import AppDateRangePicker from '../app/shared/ui/app/AppDateRangePicker.vue'
import dayjs from 'dayjs'

afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })
it('hydrates the date range with a stable Russian label despite global locale changes', async () => {
  const states = new Map<string, ReturnType<typeof ref>>()
  vi.stubGlobal('useState', (key: string, initial: () => unknown) => {
    if (!states.has(key)) states.set(key, ref(initial()))
    return states.get(key)
  })
  const view = () => h('div', [h(AppDateRangeLabel, { startDate: '2026-09-27', endDate: '2026-10-02', type: 'date' }), h(AppDateRangePicker, { modelValue: { from: '2026-09-27', to: '2026-10-02' } })])
  const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
  const error = vi.spyOn(console, 'error').mockImplementation(() => {})
  dayjs.locale('en')
  const html = await renderToString(createSSRApp(view))
  expect(html).not.toContain('Friday')
  const target = document.createElement('div')
  target.innerHTML = html
  document.body.append(target)
  dayjs.locale('ru')
  const client = createSSRApp(view)
  client.mount(target)
  await nextTick()
  expect(warn.mock.calls.filter(args => String(args[0]).includes('Hydration'))).toEqual([])
  expect(error.mock.calls.filter(args => String(args[0]).includes('Hydration'))).toEqual([])
  client.unmount()
  target.remove()
})
