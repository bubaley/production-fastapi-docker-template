# Template ownership

Products are created from this template (`make init`) and keep receiving its improvements through `/sync-template` (`.claude/skills/sync-template/`). This map decides, per path, who owns a file in a fork and what a sync does with it. **Template-owned** (this file included).

`.template-version` records where a fork stands: `repository`, `version` (template `version.json` at that point) and `commit` (template commit). `make init` writes it; every sync updates it.

## Ownership

First matching row wins (top to bottom).

| Path | Owner | Sync does |
|---|---|---|
| `backend/migrations/**` | product | Never copied. A fork keeps its own history; template model changes are re-generated in the fork (`make mm`, run by the user) |
| `frontend/openapi.json`, `frontend/app/shared/api/generated/**` | generated | Never merged: `make gen-client` after the sync |
| `backend/uv.lock`, `frontend/pnpm-lock.yaml` | generated | Re-locked after merging the manifests (`uv lock`, `pnpm install`) |
| `.template-version`, `version.json`, `CHANGELOG.md` | product | Not touched (`.template-version` is rewritten at the end of the sync) |
| `docs/product.md`, `frontend/app/app.config.ts` | product | Not touched |
| `frontend/app/features/home/**`, `frontend/app/pages/home/index.vue` | product | Not touched (demo screens a product replaces) |
| `backend/app/domains/{auth,user,organization}/**` | template | Taken from the template |
| `frontend/app/features/{auth,organization,setup,ui,user}/**` | template | Taken from the template |
| `frontend/app/pages/{auth,ui,settings}.vue`, `frontend/app/pages/settings/{index,profile}.vue`, `frontend/app/pages/settings/{organizations,users}/**`, `frontend/app/pages/home.vue`, `frontend/app/pages/home/setup/**` | template | Taken from the template |
| `frontend/app/features/landing/**`, `frontend/app/pages/index.vue` | shared | 3-way merge; the product's copy and meta win |
| `backend/app/domains/**`, `frontend/app/features/**`, `frontend/app/pages/**` | product | Not touched (product domains, features and pages) |
| `frontend/app/navigation/**`, `frontend/app/layouts/**` | shared | 3-way merge; product entries stay |
| `frontend/nuxt.config.ts`, `frontend/knip.jsonc` | shared | 3-way merge; product route rules and ignores stay |
| `backend/pyproject.toml`, `frontend/package.json` | shared | 3-way merge; product name, version and extra dependencies win |
| `.env.example`, `Makefile`, `README.md`, `compose*.yaml`, `Dockerfile`, `.github/**` | shared | 3-way merge; values written by `make init` (names, image, title) win |
| `.claude/skills/**`, `.claude/agents/**` | template | Template skills and agents are taken; a product adds its own under new names (prefix them, e.g. `.claude/skills/acme-billing/`) and those are never touched |
| everything else (`backend/app/{core,shared,scripts}/**`, `backend/app/conftest.py`, `backend/manage.py`, `frontend/app/{shared,plugins,middleware,assets}/**`, `frontend/{scripts,modules,tests}/**`, `docs/**` except `product.md`, `scripts/**`, `.claude/{hooks,settings.json}`, `AGENTS.md`, `CLAUDE.md`, configs) | template | Taken from the template |

Product code is product-owned; a fork adds files, it does not edit template-owned ones. Tests a product adds for template code go next to its own domain.

## Resolving conflicts

1. **Template-owned, unchanged in the fork** (the fork's file equals the template file at `.template-version`): take the template's new version; deleted upstream → delete.
2. **Template-owned, changed in the fork**: 3-way merge (`git merge-file`, base = template at `.template-version`). Then move the local change to an extension point if one exists (a product domain, a slot, a settings entry). If it must stay, record it under "Changes to template behavior" in [product.md](product.md) so the next sync expects it.
3. **Shared**: 3-way merge; product values win, template structure wins. Conflicts are resolved by hand, never by taking one side wholesale.
4. **Product-owned**: never touched. If a template change needs a product change (a renamed helper, a new required field), the sync reports it as a follow-up instead of editing product code silently.
5. **Generated**: regenerate (`make gen-client`, `uv lock`, `pnpm install`), never merge.
6. **Migrations**: the template's `backend/migrations/*` are never copied. When kernel models change, the fork needs its own migration: tell the user to run `make mm` and `make m`; until then verify with `PYTEST_ARGS=--sqlite`.

Template tags are fetched into `refs/template-tags/*`, never `refs/tags/*`, so the fork's release job (git-cliff) only sees the fork's own versions.

## Changing this map

A new template path that forks must not edit → add a row above (template repository). A fork that needs a different rule documents it in its `product.md` ("Changes to template behavior"); it does not edit this file.
