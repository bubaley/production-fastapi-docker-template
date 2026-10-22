---
name: add-shadcn-component
description: Add a new shadcn-vue primitive to the frontend UI kit and expose it as an App* component. Use when a screen needs a UI primitive the kit lacks (e.g. accordion, slider, command, hover card) or the user asks to add a shadcn component.
---

# Add a shadcn component

Procedure: [frontend-concept.md → Adding a shadcn primitive](../../../docs/frontend-concept.md#adding-a-shadcn-primitive).

1. Check it is really missing: `frontend/app/shared/ui/shadcn/` and `shared/ui/app/App*` (extend an App* component if one is close).
2. `cd frontend && pnpm ui:add <name>` — never `pnpm dlx shadcn-vue` directly (the script fixes the `cn` import and formats).
3. Review `shared/ui/shadcn/<name>/`: `z-50` → `z-overlay`, semantic token classes only, everything exported from `<name>/index.ts`.
4. Wrap it as `shared/ui/app/App<Name>.vue`: Russian default texts, the shared `variant`/`tone`/`size` vocabulary and control sizes (`shared/ui/app/types/control.ts`). Features use only the wrapper.
5. Add a showcase entry on `/ui` in the matching `features/ui/components/Ui*Showcase.vue` (English copy there) with its variants and states — knip fails on unused files.
6. Add the component to the Templates table in `docs/frontend-concept.md` if it is a new building block.
7. `make lint`, `/verify`, then the browser review from the `design-system` skill (both themes, 390/768/1440).
