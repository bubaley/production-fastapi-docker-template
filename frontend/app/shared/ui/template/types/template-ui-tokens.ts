export type TemplateVariant = 'page' | 'section' | 'flat-section'

export type ActionDisplayMode = 'label' | 'icon' | 'both'

export type TitleSizeToken = 'sm' | 'md' | 'lg' | 'xl'

export const weightTokens = ['light', 'regular', 'medium', 'semibold', 'bold', 'black'] as const

export type WeightToken = (typeof weightTokens)[number]
