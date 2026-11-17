/**
 * One page shell for every screen. The geometry lives in the `--page-*` tokens of `assets/styles/theme.css`
 * (responsive values included); these classes are their only consumers. Change a token, never a page.
 * The header, subheader, controls, body and footer of AppPage share one side gutter, so the title, the toolbar and the
 * content start at the same x. Vertical rhythm: header-pt → title → subheader-gap → subheader → controls-pt → controls
 * → controls-pb → body (`--page-gap` under the last pinned region in total) → content-pb.
 */
export const PAGE_GUTTER_CLASS = 'px-(--page-gutter-x)'
/** Space above the title row. */
export const PAGE_HEADER_CLASS = 'pt-(--page-header-pt)'
/** The subheader right under the title block (context, tabs, summary). */
export const PAGE_SUBHEADER_CLASS = 'pt-(--page-subheader-gap)'
/**
 * The controls bar (search, filters): a small gap above it and padding under it, so content scrolling under a pinned
 * bar never touches the fields.
 */
export const PAGE_CONTROLS_CLASS = 'pt-(--page-controls-pt) pb-(--page-controls-pb)'
/** `divided` pages: a line under the header group, one gap below its last row. */
export const PAGE_DIVIDER_CLASS = 'border-b border-border pb-(--page-gap)'
/** Default body padding: the gutter, one gap under the header, room at the bottom of the scroll. */
export const PAGE_CONTENT_CLASS = 'px-(--page-gutter-x) pt-(--page-gap) pb-(--page-content-pb)'
/** Body padding under a controls bar: its own bottom padding already counts towards the gap. */
export const PAGE_CONTENT_AFTER_CONTROLS_CLASS =
  'px-(--page-gutter-x) pt-[max(0px,calc(var(--page-gap)-var(--page-controls-pb)))] pb-(--page-content-pb)'
/** A pinned region over the scrolling body: the page surface, and a hairline that shows only once content is under it. */
export const PAGE_PINNED_CLASS = 'bg-background border-b border-transparent transition-colors data-stuck:border-border'
/** The fixed bottom region. */
export const PAGE_FOOTER_CLASS = 'border-t border-border py-(--page-footer-py)'
/**
 * A page table against the page edges: a negative margin cancels the gutter, and the edge cells take it back, so the
 * first column still lines up with the title while row lines and hover run edge to edge.
 */
export const PAGE_TABLE_BLEED_CLASS =
  '-mx-(--page-gutter-x) [&_:is(td,th):first-child]:pl-(--page-gutter-x) [&_:is(td,th):last-child]:pr-(--page-gutter-x)'
/** The h1 of a page (AppPage `title`); PageHeader renders the same through AppTitle `xl`. */
export const PAGE_TITLE_CLASS = 'text-2xl leading-tight font-semibold tracking-tight'
/** Header actions: top right of the header; on phones a full-width row under the title, start-aligned, 44px targets. */
export const PAGE_ACTIONS_CLASS =
  'flex shrink-0 flex-wrap items-center gap-2 max-md:w-full max-md:justify-start md:justify-end max-md:[&_[data-slot=button]]:min-h-[44px] max-md:[&_[data-slot=button]]:min-w-[44px]'

/** Width limit of a page (`maxWidth`): `sm` forms, `md` settings and detail pages, `lg` wide lists. */
export type PageMaxWidth = 'sm' | 'md' | 'lg'
/** Where a width-limited page sits in the free space. */
export type PageAlign = 'start' | 'center'
/**
 * What stays on screen while the body scrolls: `none` (default) — everything scrolls; `controls` — the title area
 * scrolls away and the controls bar sticks to the top; `header` — the whole header area (header, subheader, controls)
 * stays fixed. The footer is always fixed.
 */
export type PageSticky = 'none' | 'controls' | 'header'

const PAGE_MAX_WIDTH_CLASS: Record<PageMaxWidth, string> = {
  sm: 'max-w-(--page-width-sm)',
  md: 'max-w-(--page-width-md)',
  lg: 'max-w-(--page-width-lg)',
}

/** The inner column every page region shares, so a width-limited header stays aligned with its content. */
export function pageColumnClass(maxWidth?: PageMaxWidth, align: PageAlign = 'center'): string | undefined {
  if (!maxWidth) return undefined
  return ['w-full', PAGE_MAX_WIDTH_CLASS[maxWidth], align === 'center' ? 'mx-auto' : ''].filter(Boolean).join(' ')
}
