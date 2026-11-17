/**
 * The one look of every floating surface (AppMenu in all modes, select lists, date and time pickers): radius, border,
 * background, the shared `--overlay-shadow` and the inner padding. Callers only add size or padding overrides.
 */
export const OVERLAY_SURFACE_CLASS =
  'rounded-lg border border-border bg-background p-1.5 text-foreground shadow-overlay'

/** Open/close motion shared by the same surfaces. */
export const OVERLAY_MOTION_CLASS =
  'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95'
