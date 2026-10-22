import { cva, type VariantProps } from 'class-variance-authority'

// One semantic color vocabulary for every App* component (cards, labels, badges, icons, text buttons, progress).
export const TONES = ['neutral', 'muted', 'primary', 'success', 'info', 'warning', 'destructive'] as const
export type Tone = (typeof TONES)[number]

type ToneAppearance = 'text' | 'soft' | 'outline' | 'tinted' | 'solid' | 'stroke'

// Full class names stay literal so Tailwind can find them.
const TONE_CLASSES: Record<Tone, Record<ToneAppearance, string>> = {
  neutral: {
    text: 'text-foreground',
    soft: 'bg-muted/60 text-foreground',
    outline: 'border-border text-foreground',
    tinted: 'border-border bg-card',
    solid: 'bg-foreground text-background',
    stroke: 'stroke-foreground',
  },
  muted: {
    text: 'text-muted-foreground',
    soft: 'bg-muted/60 text-muted-foreground',
    outline: 'border-border text-muted-foreground',
    tinted: 'border-border bg-muted/50',
    solid: 'bg-muted text-muted-foreground',
    stroke: 'stroke-muted-foreground',
  },
  primary: {
    text: 'text-primary',
    soft: 'bg-primary/12 text-primary',
    outline: 'border-primary/45 text-primary',
    tinted: 'border-primary/45 bg-primary/10',
    solid: 'bg-primary text-primary-foreground',
    stroke: 'stroke-primary',
  },
  success: {
    text: 'text-success',
    soft: 'bg-success/12 text-success',
    outline: 'border-success/45 text-success',
    tinted: 'border-success/45 bg-success/10',
    solid: 'bg-success text-success-foreground',
    stroke: 'stroke-success',
  },
  info: {
    text: 'text-info',
    soft: 'bg-info/12 text-info',
    outline: 'border-info/45 text-info',
    tinted: 'border-info/45 bg-info/10',
    solid: 'bg-info text-info-foreground',
    stroke: 'stroke-info',
  },
  warning: {
    text: 'text-warning',
    soft: 'bg-warning/12 text-warning',
    outline: 'border-warning/45 text-warning',
    tinted: 'border-warning/45 bg-warning/10',
    solid: 'bg-warning text-warning-foreground',
    stroke: 'stroke-warning',
  },
  destructive: {
    text: 'text-destructive',
    soft: 'bg-destructive/12 text-destructive',
    outline: 'border-destructive/45 text-destructive',
    tinted: 'border-destructive/45 bg-destructive/10',
    solid: 'bg-destructive text-destructive-foreground',
    stroke: 'stroke-destructive',
  },
}

const APPEARANCES = Object.keys(TONE_CLASSES.neutral) as ToneAppearance[]

/**
 * `toneVariants({ tone: 'success', appearance: 'soft' })`.
 * `text` colors text/icons, `soft` adds a tint, `outline` a matching border color, `tinted` is a card surface,
 * `solid` a filled badge/button, `stroke` an SVG stroke. Without `tone` nothing is applied (inherits).
 */
export const toneVariants = cva('', {
  variants: {
    tone: Object.fromEntries(TONES.map((tone) => [tone, ''])) as Record<Tone, string>,
    appearance: Object.fromEntries(APPEARANCES.map((appearance) => [appearance, ''])) as Record<ToneAppearance, string>,
  },
  compoundVariants: TONES.flatMap((tone) =>
    APPEARANCES.map((appearance) => ({ tone, appearance, class: TONE_CLASSES[tone][appearance] })),
  ),
  defaultVariants: { appearance: 'text' },
})

export type ToneVariants = VariantProps<typeof toneVariants>

export const isTone = (value: unknown): value is Tone => TONES.includes(value as Tone)
