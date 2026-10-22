---
name: design-system
description: Build or restyle frontend UI the way this template's design system requires — tokens, palettes, App* components, Russian copy — and visually review it in the browser. Use for any change to screens, components, styling, colors, theming, spacing or layout in frontend/, and before finishing UI work.
---

# Design system

Rules: [frontend-concept.md](../../../docs/frontend-concept.md) — Design system, Templates, UI layers and visual review, Button and table variants. Live reference: `/ui`.

**Build**
1. Compose screens from `AppPageView`, `AppListTemplate`/`AppDetailTemplate`, `AppSection`, `AppCard` and other `App*` components. Features never import `reka-ui` or `shared/ui/shadcn` (the architecture guard fails).
2. Missing primitive? Extend an `App*` component; a genuinely new one → `add-shadcn-component` skill.
3. Colors, radii, sizes only through tokens from `app/assets/styles/theme.css` via utilities (`bg-card`, `text-success`, `h-control-md`, `z-overlay`). No hex values, no `bg-[color:var(--…)]`, no inline geometry styles.
4. One vocabulary: `variant`, `tone` (`success`/`info`/`warning`/`destructive`), `size` (`xs`–`lg`). Two or more buttons in a row → `AppTemplateActions`; a single async click → `useActionState`.
5. Icons: `@lucide/vue` components. Dates: `useDate()`.
6. Copy: **Russian** for product screens (titles, labels, empty states, toasts, errors). `/ui` is the only English screen.
7. Re-branding (palette, neutral surfaces): "Re-branding a fork" in the doc; check `/ui` → Tokens.

**Review in the browser** (required; checks do not replace it)
1. `make run-backend` + `make run-frontend` (or use running servers); open the affected screens and `/ui`.
2. Each screen at **390, 768 and 1440 px**, in **light and dark**, and with a non-default palette when colors changed.
3. Walk the checklist in "UI layers and visual review": empty/loading/error/retry, long text, disabled/loading buttons, modals and drawers (stacking, Escape, focus return), no horizontal page scroll or double scrollbars, no console errors or hydration warnings after reload.
4. Report what you looked at and what you fixed; the `ui-reviewer` subagent can do this pass on a diff.
