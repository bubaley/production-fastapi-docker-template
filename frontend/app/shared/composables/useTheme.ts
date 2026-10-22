import { computed } from 'vue'
import {
  DEFAULT_PALETTE,
  PALETTE_COOKIE,
  PALETTES,
  THEME_MODES,
  isPalette,
  isThemeMode,
  type Palette,
  type ThemeMode,
} from '~/shared/lib/theme'

/**
 * Color mode (system / light / dark, via @nuxtjs/color-mode) and brand palette.
 * The palette lives in a cookie so SSR renders `<html data-palette>` without a flash; app.vue applies it.
 */
export const useTheme = () => {
  const colorMode = useColorMode()
  const paletteCookie = useCookie<string | null>(PALETTE_COOKIE, {
    default: () => DEFAULT_PALETTE,
    maxAge: 60 * 60 * 24 * 365,
    sameSite: 'lax',
  })

  const mode = computed<ThemeMode>({
    get: () => (isThemeMode(colorMode.preference) ? colorMode.preference : 'system'),
    set: (value) => {
      colorMode.preference = value
    },
  })
  /** The theme actually shown: `system` resolved to light or dark. */
  const resolvedMode = computed<'light' | 'dark'>(() => (colorMode.value === 'dark' ? 'dark' : 'light'))
  // Shared state keeps every consumer in sync; the cookie only persists it.
  const paletteState = useState<Palette>('app-palette', () =>
    isPalette(paletteCookie.value) ? paletteCookie.value : DEFAULT_PALETTE,
  )
  const palette = computed<Palette>({
    get: () => paletteState.value,
    set: (value) => {
      const next = isPalette(value) ? value : DEFAULT_PALETTE
      paletteState.value = next
      paletteCookie.value = next
    },
  })

  return { mode, resolvedMode, palette, modes: THEME_MODES, palettes: PALETTES }
}
