import type { ButtonVariants } from '~/shared/ui/shadcn/button'
import { cn } from '~/shared/lib/utils'
import type { AppButtonSize } from './types/control'

export type AppButtonVariant = 'default' | 'secondary' | 'outline' | 'ghost' | 'link' | 'destructive'
export type AppButtonTextVariant = 'base' | 'muted'

/** Icon-only buttons take the square size of the same row height. */
export function resolveAppButtonSize(size: AppButtonSize, iconOnly: boolean): AppButtonSize {
  if (!iconOnly) return size
  return ({ xs: 'icon-xs', sm: 'icon-sm', md: 'icon', lg: 'icon-lg' } as const)[size as 'xs'] ?? size
}

// `muted` text stays muted at rest and takes the variant's own text color on hover and keyboard focus.
const mutedHover: Record<AppButtonVariant, string> = {
  default: 'hover:text-primary-foreground focus-visible:text-primary-foreground',
  destructive: 'hover:text-destructive-foreground focus-visible:text-destructive-foreground',
  secondary: 'hover:text-secondary-foreground focus-visible:text-secondary-foreground',
  link: 'hover:text-primary focus-visible:text-primary',
  outline: 'hover:text-foreground focus-visible:text-foreground',
  ghost: 'hover:text-foreground focus-visible:text-foreground',
}

export const appButtonPrimitiveSize = (size: AppButtonSize) =>
  (size === 'md' ? 'default' : size) as NonNullable<ButtonVariants['size']>

/** Classes AppButton adds on top of the shadcn `buttonVariants` for its variant and size. */
export function appButtonExtraClasses(options: {
  variant?: AppButtonVariant
  textVariant?: AppButtonTextVariant
  fluid?: boolean
}) {
  return cn(
    'cursor-pointer disabled:pointer-events-auto disabled:cursor-not-allowed',
    options.textVariant === 'muted' && ['text-muted-foreground', mutedHover[options.variant ?? 'default']],
    options.fluid && 'w-full',
  )
}
