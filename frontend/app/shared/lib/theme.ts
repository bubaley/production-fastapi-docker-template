// Theme constants shared by nuxt.config (inline head script) and useTheme. Keep this file free of Nuxt imports.
export const THEME_MODES = ['system', 'light', 'dark'] as const
export type ThemeMode = (typeof THEME_MODES)[number]

// Must match the `[data-palette=…]` blocks in assets/styles/theme.css.
export const PALETTES = ['neutral', 'blue', 'violet', 'green', 'orange'] as const
export type Palette = (typeof PALETTES)[number]

export const DEFAULT_PALETTE: Palette = 'violet'
export const PALETTE_COOKIE = 'palette'
export const COLOR_MODE_COOKIE = 'colorScheme'

export const isPalette = (value: unknown): value is Palette => PALETTES.includes(value as Palette)

export const isThemeMode = (value: unknown): value is ThemeMode => THEME_MODES.includes(value as ThemeMode)

/** Applies the palette cookie before the first paint, including client-only routes without SSR markup. */
export const paletteHeadScript = `(function(){try{var m=document.cookie.match(/(?:^|; )${PALETTE_COOKIE}=([^;]*)/);var p=m&&decodeURIComponent(m[1]);if(${JSON.stringify(PALETTES)}.indexOf(p)>-1)document.documentElement.setAttribute('data-palette',p)}catch(e){}})()`
