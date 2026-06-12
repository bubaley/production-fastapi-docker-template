export type TemplateVariant = 'page' | 'section' | 'flat-section'


export type ActionDisplayMode = 'label' | 'icon' | 'both'

export const colorTokens = [
  'primary',
  'cloud',
  'secondary',
  'info',
  'danger',
  'success',
  'accent',
  'orange',
  'yellow',
  'teal',
  'pink',
] as const

export type ColorToken = (typeof colorTokens)[number]

export const blockVariants = ['filled', 'ghost', 'outlined', 'ghost-outlined', 'text'] as const

export type BlockVariantToken = (typeof blockVariants)[number]

export type RadiusToken = 'sm' | 'md' | 'lg' | 'full' | 'unset'

export type TitleSizeToken = 'sm' | 'md' | 'lg' | 'xl'

export type SizeToken =
  | 'xs'
  | 'sm'
  | 'md'
  | 'lg'
  | 'xl'
  | '2xl'
  | '3xl'
  | '4xl'
  | '5xl'
  | '6xl'
  | '7xl'
  | '8xl'
  | '9xl'
  | '10xl'

export const weightTokens = ['light', 'regular', 'medium', 'semibold', 'bold', 'black'] as const

export type WeightToken = (typeof weightTokens)[number]
