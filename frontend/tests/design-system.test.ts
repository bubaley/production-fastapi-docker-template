import { afterEach, describe, expect, it, vi } from 'vite-plus/test'
import { mount } from '@vue/test-utils'
import { h, reactive, ref } from 'vue'
import { Plus } from '@lucide/vue'
import AppButton from '../app/shared/ui/app/AppButton.vue'
import { resolveAppButtonSize } from '../app/shared/ui/app/appButton'
import { TONES, toneVariants } from '../app/shared/ui/app/tone'
import { deepClone } from '../app/shared/lib/clone'
import { cn } from '../app/shared/lib/utils'
import { DEFAULT_PALETTE, PALETTES, paletteHeadScript } from '../app/shared/lib/theme'
import { useTheme } from '../app/shared/composables/useTheme'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('tone map', () => {
  it('maps every tone and appearance to literal token classes', () => {
    expect(toneVariants({ tone: 'success' })).toBe('text-success')
    expect(toneVariants({ tone: 'destructive', appearance: 'soft' })).toBe('bg-destructive/12 text-destructive')
    expect(toneVariants({ tone: 'primary', appearance: 'tinted' })).toBe('border-primary/45 bg-primary/10')
    expect(toneVariants({ tone: 'warning', appearance: 'solid' })).toBe('bg-warning text-warning-foreground')
    expect(toneVariants({})).toBe('')
    for (const tone of TONES) expect(toneVariants({ tone, appearance: 'outline' })).toMatch(/^border-/)
  })
  it('keeps custom scales when merging classes', () => {
    expect(cn('text-foreground', 'text-control-sm')).toBe('text-foreground text-control-sm')
    expect(cn('h-9', 'h-control-md')).toBe('h-control-md')
    expect(cn('shadow-md', 'shadow-overlay')).toBe('shadow-overlay')
  })
})

describe('AppButton', () => {
  const render = (props: Record<string, unknown>, slot?: string) => {
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    return mount(AppButton, { props, slots: slot ? { default: () => h('span', slot) } : undefined })
  }

  it('maps variant and size to token-based classes', () => {
    const classes = render({ label: 'Save', size: 'sm', variant: 'outline' }).get('button').classes()
    expect(classes).toEqual(expect.arrayContaining(['h-control-sm', 'px-3', 'text-control-sm', 'border-input']))
    expect(render({ label: 'Save' }).get('button').classes()).toEqual(
      expect.arrayContaining(['h-control-md', 'bg-primary', 'text-primary-foreground']),
    )
    expect(render({ label: 'Delete', variant: 'destructive' }).get('button').classes()).toContain('bg-destructive')
  })
  it('renders icon-only buttons as squares of the same row height', () => {
    const button = render({ icon: Plus, size: 'sm', 'aria-label': 'Add' }).get('button')
    expect(button.classes()).toContain('size-control-sm')
    expect(button.attributes('aria-label')).toBe('Add')
    expect(button.attributes('style')).toBeUndefined()
    expect(resolveAppButtonSize('lg', true)).toBe('icon-lg')
    expect(resolveAppButtonSize('icon-xs', true)).toBe('icon-xs')
    expect(resolveAppButtonSize('md', false)).toBe('md')
  })
  it('keeps muted text until hover and disables while loading', () => {
    const button = render({ label: 'Muted', variant: 'ghost', textVariant: 'muted', loading: true }).get('button')
    expect(button.classes()).toEqual(expect.arrayContaining(['text-muted-foreground', 'hover:text-foreground']))
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.attributes('aria-busy')).toBe('true')
  })
})

describe('useTheme', () => {
  const setup = (cookieValue: string | null, preference = 'system') => {
    const cookie = ref<string | null>(cookieValue)
    const states = new Map<string, ReturnType<typeof ref>>()
    const colorMode = reactive({ preference, value: preference === 'dark' ? 'dark' : 'light' })
    vi.stubGlobal('useColorMode', () => colorMode)
    vi.stubGlobal('useCookie', () => cookie)
    vi.stubGlobal('useState', (key: string, initial: () => unknown) => {
      if (!states.has(key)) states.set(key, ref(initial()))
      return states.get(key)
    })
    return { cookie, colorMode }
  }

  it('reads the palette cookie and persists changes', () => {
    const { cookie } = setup('violet')
    const theme = useTheme()
    expect(theme.palette.value).toBe('violet')
    theme.palette.value = 'green'
    expect(cookie.value).toBe('green')
    expect(useTheme().palette.value).toBe('green')
  })
  it('falls back to the default palette for unknown values', () => {
    const { cookie } = setup('pink')
    const theme = useTheme()
    expect(theme.palette.value).toBe(DEFAULT_PALETTE)
    theme.palette.value = 'pink' as never
    expect(cookie.value).toBe(DEFAULT_PALETTE)
  })
  it('switches the color mode preference', () => {
    const { colorMode } = setup(null, 'dark')
    const theme = useTheme()
    expect(theme.mode.value).toBe('dark')
    expect(theme.resolvedMode.value).toBe('dark')
    theme.mode.value = 'system'
    expect(colorMode.preference).toBe('system')
  })
  it('applies only known palettes from the head script', () => {
    for (const value of ['blue', 'evil"'] as const) {
      document.documentElement.removeAttribute('data-palette')
      document.cookie = `palette=${encodeURIComponent(value)}; path=/`
      new Function(paletteHeadScript)()
      expect(document.documentElement.getAttribute('data-palette')).toBe(
        PALETTES.includes(value as never) ? value : null,
      )
    }
  })
})

describe('deepClone', () => {
  it('copies plain data and unwraps nested reactive proxies', () => {
    const nested = reactive({ tags: ['a'], at: new Date(0) })
    const source = reactive({ name: 'x', nested, list: [reactive({ id: 1 })] })
    const copy = deepClone(source)
    expect(copy).toEqual({ name: 'x', nested: { tags: ['a'], at: new Date(0) }, list: [{ id: 1 }] })
    copy.nested.tags.push('b')
    expect(nested.tags).toEqual(['a'])
    expect(() => structuredClone(copy)).not.toThrow()
  })
})
