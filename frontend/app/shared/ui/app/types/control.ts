import type { CSSProperties } from 'vue'
import type { AppIconSize } from '../AppIcon.vue'
export type AppFieldVariant = 'outline' | 'secondary' | 'ghost' | 'active-outline'
export const appControlIconSize: Record<AppButtonSize, AppIconSize> = {
  xs: 'xs',
  sm: 'sm',
  default: 'sm',
  lg: 'md',
  'icon-xs': 'xs',
  'icon-sm': 'sm',
  icon: 'sm',
  'icon-lg': 'lg',
}

export type AppControlSize = 'xs' | 'sm' | 'default' | 'lg'
export type AppButtonSize = AppControlSize | 'icon-xs' | 'icon-sm' | 'icon' | 'icon-lg'

export const appControlRadiusClasses: Record<AppButtonSize, string> = {
  xs: 'rounded-sm',
  sm: 'rounded-md',
  default: 'rounded-md',
  lg: 'rounded-md',
  'icon-xs': 'rounded-sm',
  'icon-sm': 'rounded-md',
  icon: 'rounded-md',
  'icon-lg': 'rounded-md',
}

// Edit shared control geometry here. Components below only consume the resulting styles.
const height: Record<AppControlSize, string> = {
  xs: '22px',
  sm: '26px',
  default: '2.25rem',
  lg: '2.5rem',
}
const inputPaddingX: Record<AppControlSize, string> = {
  xs: '0.5rem',
  sm: '0.625rem',
  default: '0.75rem',
  lg: '0.875rem',
}
const selectPaddingX: Record<AppControlSize, string> = {
  xs: '0.375rem',
  sm: '0.5rem',
  default: '0.5rem',
  lg: '0.75rem',
}
const selectPaddingY: Record<AppControlSize, string> = {
  xs: '0',
  sm: '0.125rem',
  default: '0.25rem',
  lg: '0.375rem',
}
const buttonPaddingX: Record<AppControlSize, string> = {
  xs: '0.625rem',
  sm: '0.75rem',
  default: '1rem',
  lg: '1.5rem',
}
const fieldFontSize: Record<AppControlSize, string> = {
  xs: '0.75rem',
  sm: '0.8525rem',
  default: '0.875rem',
  lg: '0.875rem',
}
const buttonFontSize: Record<AppControlSize, string> = {
  xs: '0.75rem',
  sm: '0.8525rem',
  default: '0.875rem',
  lg: '0.875rem',
}

const input = Object.fromEntries(
  (Object.keys(height) as AppControlSize[]).map((size) => [
    size,
    { height: height[size], paddingInline: inputPaddingX[size], fontSize: fieldFontSize[size], lineHeight: '1.25' },
  ]),
) as Record<AppControlSize, CSSProperties>

const select = Object.fromEntries(
  (Object.keys(height) as AppControlSize[]).map((size) => [
    size,
    { minHeight: height[size], paddingInline: selectPaddingX[size] },
  ]),
) as Record<AppControlSize, CSSProperties>

const selectValue = Object.fromEntries(
  (Object.keys(height) as AppControlSize[]).map((size) => [
    size,
    { paddingBlock: selectPaddingY[size], fontSize: fieldFontSize[size], lineHeight: '1.25' },
  ]),
) as Record<AppControlSize, CSSProperties>

const button: Record<AppButtonSize, CSSProperties> = {
  ...Object.fromEntries(
    (Object.keys(height) as AppControlSize[]).map((size) => [
      size,
      {
        height: height[size],
        paddingInline: buttonPaddingX[size],
        fontSize: buttonFontSize[size],
        lineHeight: '1.25',
        paddingBlock: '0',
      },
    ]),
  ),
  'icon-xs': { width: height.xs, height: height.xs },
  'icon-sm': { width: height.sm, height: height.sm },
  icon: { width: height.default, height: height.default },
  'icon-lg': { width: height.lg, height: height.lg },
} as Record<AppButtonSize, CSSProperties>

export const appControlStyles = { button, input, select, selectValue }

export const activeOutlineClasses = 'border-primary bg-primary/10 text-primary hover:bg-primary/20'

export const appSelectIconSize: Record<AppControlSize, AppIconSize> = { xs: 'xs', sm: 'xs', default: 'sm', lg: 'md' }
