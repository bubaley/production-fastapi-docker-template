import type { AppIconSize } from '../AppIcon.vue'

// Shared control vocabulary. Heights and text sizes come from the `--size-control-*` / `--font-size-control-*`
// tokens in theme.css (utilities `h-control-*`, `text-control-*`); change geometry there, not here.
export type AppControlSize = 'xs' | 'sm' | 'md' | 'lg'
export type AppButtonSize = AppControlSize | 'icon-xs' | 'icon-sm' | 'icon' | 'icon-lg'
export type AppFieldVariant = 'outline' | 'secondary' | 'ghost' | 'active-outline'

export const appControlIconSize: Record<AppButtonSize, AppIconSize> = {
  xs: 'xs',
  sm: 'sm',
  md: 'sm',
  lg: 'md',
  'icon-xs': 'xs',
  'icon-sm': 'sm',
  icon: 'sm',
  'icon-lg': 'lg',
}

export const appSelectIconSize: Record<AppControlSize, AppIconSize> = { xs: 'xs', sm: 'xs', md: 'sm', lg: 'md' }

/** Text inputs: fixed height, horizontal padding, font size and radius. */
export const appInputSizeClasses: Record<AppControlSize, string> = {
  xs: 'h-control-xs rounded-sm px-2 text-control-xs',
  sm: 'h-control-sm rounded-md px-2.5 text-control-sm',
  md: 'h-control-md rounded-md px-3 text-control-md',
  lg: 'h-control-lg rounded-md px-3.5 text-control-md',
}

/** Select-like triggers grow with chips, so they get a minimum height. */
export const appSelectSizeClasses: Record<AppControlSize, string> = {
  xs: 'min-h-control-xs rounded-sm px-1.5',
  sm: 'min-h-control-sm rounded-md px-2',
  md: 'min-h-control-md rounded-md px-2',
  lg: 'min-h-control-lg rounded-md px-3',
}

export const appSelectValueSizeClasses: Record<AppControlSize, string> = {
  xs: 'py-0 text-control-xs',
  sm: 'py-0.5 text-control-sm',
  md: 'py-1 text-control-md',
  lg: 'py-1.5 text-control-md',
}

/** Exposes the control height as `--control-size` for compound controls (filter chips, square add buttons). */
export const appControlSizeVar: Record<AppControlSize, string> = {
  xs: '[--control-size:var(--size-control-xs)]',
  sm: '[--control-size:var(--size-control-sm)]',
  md: '[--control-size:var(--size-control-md)]',
  lg: '[--control-size:var(--size-control-lg)]',
}

export const activeOutlineClasses = 'border-primary bg-primary/10 text-primary hover:bg-primary/20'
