---
name: design-system
description: Build or restyle frontend UI the way this template's design system requires — tokens, palettes, App* components, Russian copy — add missing shadcn-vue primitives, and visually review the result in the browser. Use for any change to screens, components, styling, colors, theming, spacing or layout in frontend/, when a screen needs a UI primitive the kit lacks (accordion, slider, command, hover card…), and before finishing UI work.
---

# Design system

Rules: [frontend-concept.md](../../../docs/frontend-concept.md) — Design system, Templates, UI layers and visual review, Button and table variants. Live reference: `/ui`.

**Build**
1. Compose screens from `AppPageView`, `AppListTemplate`/`AppDetailTemplate`, `AppSection`, `AppCard` and other `App*` components. Features never import `reka-ui` or `shared/ui/shadcn` (the architecture guard fails).
2. Missing primitive? Extend a close `App*` component first; a genuinely new one → "Add a shadcn primitive" below.
3. Colors, radii, sizes only through tokens from `app/assets/styles/theme.css` via utilities (`bg-card`, `text-success`, `h-control-md`, `z-overlay`). No hex values, no `bg-[color:var(--…)]`, no inline geometry styles.
4. One vocabulary: `variant`, `tone` (`success`/`info`/`warning`/`destructive`), `size` (`xs`–`lg`). Two or more buttons in a row → `AppTemplateActions`; a single async click → `useActionState`.
5. Data through resource descriptors and Pinia Colada, never `useFetch`/`$fetch` for API resources. Icons: `@lucide/vue` components. Dates: `useDate()`.
6. Copy: **Russian** for product screens (titles, labels, placeholders, empty states, toasts, errors, aria-labels). `/ui` is the only English screen.
7. Re-branding (palette, neutral surfaces): "Re-branding a fork" in the doc; check `/ui` → Tokens.

**Add a shadcn primitive** — procedure: [frontend-concept.md → Adding a shadcn primitive](../../../docs/frontend-concept.md#adding-a-shadcn-primitive).
1. Confirm it is missing in `frontend/app/shared/ui/shadcn/` and `shared/ui/app/App*`.
2. `cd frontend && pnpm ui:add <name>` — never `pnpm dlx shadcn-vue` directly (the script fixes the `cn` import and formats).
3. Review `shared/ui/shadcn/<name>/`: `z-50` → `z-overlay`, semantic token classes only, everything exported from `<name>/index.ts`.
4. Wrap it as `shared/ui/app/App<Name>.vue`: Russian default texts, the shared vocabulary and control sizes (`shared/ui/app/types/control.ts`). Features use only the wrapper.
5. Showcase it on `/ui` in the matching `features/ui/components/Ui*Showcase.vue` (English) with variants and states — knip fails on unused files. New building block → add it to the Templates table in the doc.

**Review in the browser** (required; `make check` does not replace it)
1. `make run-backend` + `make run-frontend` (or reuse running servers), sign in at `/auth`. Map the diff (`git diff HEAD -- frontend/app`) to routes: `pages/**` → its route, feature views → the pages that mount them, `shared/ui/**` → `/ui` plus every screen using the component.
2. Each affected route at **390, 768 and 1440 px**, in **light and dark**, and with a non-default palette when colors changed.
3. Walk "UI layers and visual review" in the doc: empty/loading/error/retry, long text, create/edit/delete, disabled/loading buttons, modals and drawers (stacking, Escape, focus return), no horizontal page scroll, double scrollbars or overlapping fixed regions, no console errors or hydration warnings after reload.
4. Report the routes, viewports and themes you checked and what you fixed; say plainly if no browser was available.
