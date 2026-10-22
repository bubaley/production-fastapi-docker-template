# Architecture

Full-stack template: FastAPI REST API (`/api/v1`) + Nuxt 4 app with hybrid rendering (client-only app routes, SSR for public pages). FastAPI owns auth (HttpOnly cookies); the frontend talks to it through a client generated from the OpenAPI schema. Data is scoped by the current user and organization (`FilterObjectsManager` on the backend, `Organization-Key` on the frontend).

What the app does: [template-core.md](template-core.md) (inherited by every product) and [product.md](product.md) (this product; wins on conflict). Who owns which path in a fork: [template-ownership.md](template-ownership.md).

| Layer | Stack |
|---|---|
| Backend | Python 3.15, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, Pinia Colada, `@hey-api/openapi-ts` (generated client), shadcn-vue / Reka UI, Tailwind CSS |
| Infra | One Docker image (s6-overlay: Caddy, uvicorn, Nuxt, Taskiq), Docker Compose, GitHub Actions, Makefile — see [deployment.md](deployment.md) |

**Where to put new code**

- Business capability (CRUD entity, org, user) → a **domain** on the backend and a **feature** on the frontend. Same name when possible (`organization` / `organization`).
- Cross-cutting infrastructure (auth kernel, S3, base viewset) → `backend/app/core/` or `frontend/app/shared/`.
- Pages are thin: they only mount a feature view. Layouts own navigation.

Canonical examples: `backend/app/domains/organization/`, `frontend/app/features/organization/`. Live UI primitives: `/ui` (public static catalogue). The catalogue uses local sample data and does not expose organization resources.

`AppPageView` combines `AppPage` and `PageHeader` for one page heading and a bounded scrolling body. The fixed regions are header, subheader before the divider, controls after the divider, and footer; HomeView demonstrates them. `AppSection` groups content structurally; use `AppCard` for a visible surface. App controls share one set of control sizes (`shared/ui/app/types/control.ts`) and semantic light/dark tokens. Feature data goes through resource descriptors over the generated client.

### New capability — definition of done

Same change, all of this (skip a row only if it does not apply):

| Layer | Done when |
|---|---|
| Backend | Domain files (`models`, `schemas`, `filters`, `views` exporting `routers`) — `make new-domain name=<snake_name>` scaffolds them with the frontend feature; models and routers are auto-discovered. Declare **`tenant_scope`** on every model. Views stay thin — workflows in a **service** (instances in, not ids). See [backend-concept.md](backend-concept.md#services-vs-viewsets-vs-utils) |
| Tests | Non-trivial rules get pytest next to the domain (`domains/<name>/tests/`). See [backend-concept.md](backend-concept.md#tests). Canonical: `domains/organization/tests/test_organization.py` |
| Frontend | `make gen-client` (schema + generated client committed), feature resource descriptor, views on `AppListTemplate` / `AppDetailTemplate`, thin page, drawer item if needed. User-facing copy in **Russian** |
| Realtime | Org events go through **`OrganizationWebSocketService`**, not a new websocket stack |
| Docs | [product.md](product.md) if the user can see or do something new ([template-core.md](template-core.md) for inherited capabilities in the template repo). Concept docs if the pattern itself changed |
| Checks | `make lint` applied, `make check` is green |
| Migration | Tell the user `make mm` / `make m` is needed. Do not run it unless they ask (the hook blocks it; `ALLOW_MIGRATIONS=1` after an explicit yes) |

---

## Backend tree

```
backend/app/
  main.py                 # FastAPI app: middleware, discovered /api/v1 routers, /ws, /health
  conftest.py             # Shared pytest fixtures: `db` on a PostgreSQL test database (`--sqlite` for in-memory, `--keepdb` to reuse)
  core/                   # Application kernel — not a business domain
  domains/                # One folder per business module
  shared/                 # Cross-domain services, utils, permissions
  scripts/                # CLI one-offs (create_superuser, …)
```

### `core/` — kernel

Owns process-wide wiring. Do not put organization/user business rules here.

| Path | Why it exists |
|---|---|
| `settings.py` | Env-backed config |
| `database.py` | Tortoise ORM setup; `MODELS` comes from `discovery.py` |
| `discovery.py` | Finds domains: `domains/*/models.py` → `MODELS`, `domains/*/views.py` `routers` → `/api/v1` (kernel domains first, then alphabetical; import errors fail loudly) |
| `auth.py` | Credential resolution (cookie → `Token` → `Bearer`), current user / org (`AuthState`) |
| `csrf.py` | Trusted-origin check for cookie-authenticated unsafe requests and websocket handshakes |
| `openapi.py` | OpenAPI conventions: operationIds, error responses, security schemes (`make openapi` → `frontend/openapi.json`) |
| `viewsets.py` | `BaseModelViewSet` / `BaseReadOnlyViewSet` — auth, pagination, scoping |
| `models.py` | `BaseModel` (`id`, `created_at`, `updated_at`) and base schemas |
| `broker.py` | Taskiq |
| `exceptions.py` | Exception handlers |
| `services/` | Infrastructure **classes** (S3, crypto, logger, websocket) |
| `utils/` | Small **functions** (dates, exception details) |
| `fields/` | Reusable Tortoise/Pydantic fields |
| `tests/` | App-level tests (health, auth smoke) — not domain tests |

`core/services/websocket_service.py` is the single websocket transport. Secure
channels deny access until a domain supplies an explicit policy.
`OrganizationWebSocketService` reuses `core/auth.py` credential resolution (the
access cookie for browsers) and
checks membership before accepting a connection. Business membership workflows
live in `domains/organization/services/organization_service.py`.

### `domains/<name>/` — business module

One domain can contain several models. Split files by role, not by putting everything in `views.py`.

| Path | Why it exists |
|---|---|
| `models.py` | Tortoise models for this domain |
| `schemas.py` | Create / update / read DTOs (`@schema(model=…)`) |
| `filters.py` | fastapi-ronin `FilterSet` (list search/filter) |
| `views.py` | Routers + viewsets (HTTP), exports `routers = (…)`. Keep this thin — call services for non-CRUD logic |
| `services/` | Domain **classes** (see services vs utils below) |
| `tests/` | Tests for this domain: `tests/test_<subject>.py` |

No registration step: `core/discovery.py` picks up `models.py` and the `routers` exported by `views.py`. Declare `tenant_scope` on each model (queryset scope, see [backend-concept.md](backend-concept.md#scoping)).

### `shared/` — used by more than one domain

| Path | Why it exists |
|---|---|
| `services/` | Cross-domain **classes** (`FilterObjectsManager`, entity resolver, …) |
| `utils/` | Cross-domain **functions** |
| `permissions/` | Reusable permission classes (`IsSuperuser`, …) |

If only one domain needs it, keep it in that domain.

### Services vs utils

| | `services/` | `utils/` |
|---|---|---|
| Shape | **Classes only** (state, collaborators, a named responsibility) | **Functions** — small, mostly pure helpers |
| Size | One class → `services/foo_service.py`. If the class grows, make a package: `services/foo_service/foo_service.py` plus private modules used only by that class | One concern per module, e.g. `date_utils.py` |
| Do not | Put free functions in `services/` | Put a god-module of mixed class + helpers in `utils/` |

```
# small
services/organization_service.py

# grown class — package next to the class, not a dumping ground
services/invoice_builder/
  invoice_builder.py      # class InvoiceBuilder
  line_items.py           # helpers used only by InvoiceBuilder
```

---

## Frontend tree

```
frontend/
  openapi.json            # API contract, written by `make openapi`
  openapi-ts.config.ts    # `pnpm gen:api`: generated client into app/shared/api/generated/
  colada.options.ts       # Pinia Colada defaults (staleTime)
  modules/dev-proxy.ts    # `nuxt dev` only: /api/v1 and /ws on the Nuxt origin -> FastAPI
frontend/app/
  features/               # One folder per business module (mirrors a backend domain)
  pages/                  # Nuxt routes — thin wrappers over feature views
  layouts/                # Shell + drawer navigation (default, settings, setup, auth)
  navigation/             # Drawer entries as data (settings.ts)
  shared/                 # API layer, UI kit, composables, utils
  middleware/             # Session and organization guards (page meta `auth`, `organization`)
  plugins/                # `$api`: the generated client per app instance
  app.config.ts           # Product name (header, public page, meta tags)
```

### `features/<name>/`

| Path | Why it exists |
|---|---|
| `resources/` | One **entity per file**: type aliases over the generated schemas, the form type and `defineResource({ key, sdk, toForm, toCreate, toUpdate })`. `organization.ts` and `organizationUser.ts` stay separate |
| `views/` | Screen-level UI: list page, detail page, or a large section used as a page. Built on `AppListTemplate` / `AppDetailTemplate` with `:resource` |
| `components/` | Pieces used by those views. Split early — views should not grow into god-files |
| `composables/` | Feature-wide logic used by **several** views/components (`useOrganization`) |

**Related UI lives together.** A standalone widget is a single file. A cluster of tightly coupled pieces gets a folder; composables that exist only for that cluster go in the same folder (not in the feature-wide `composables/`):

```
components/OrganizationPicker.vue          # one widget

components/member-list/                    # one concern, several files
  OrganizationMembersList.vue
  MemberRoleSelect.vue
  useMemberList.ts

composables/useOrganization.ts             # shared across the whole feature
```

Same idea already exists in the UI kit: `shared/ui/app/date-picker/` (components + local composables).

### `pages/` and `layouts/`

| Path | Why it exists |
|---|---|
| `pages/**/*.vue` | Route only. Import a feature view; no business logic, no API calls. `definePageMeta({ auth: false })` marks a public page |
| `layouts/*.vue` | Chrome and **drawer items**. Nuxt route names come from the file path: `settings/organizations/[id].vue` → `settings-organizations-id` |
| `navigation/settings.ts` | Settings drawer entries as data (`settingsNavigation`); `make new-domain` appends to it |

Rendering is hybrid (`routeRules` in `nuxt.config.ts`): app routes (`/home/**`, `/settings/**`, `/auth`, `/ui`) render in the browser; public pages (`/`) render on the server with SEO meta. See [frontend-concept.md](frontend-concept.md#rendering).

### `shared/`

| Path | Why it exists |
|---|---|
| `api/generated/` | Written by `pnpm gen:api`; never edited by hand |
| `api/` | `client.ts` (client factory, `ApiError`, 401 refresh-and-retry), `resource.ts` (descriptor, query keys, page/save helpers), `useResource.ts` (Pinia Colada list/item/mutations, `useApiClient`) |
| `ui/app/` | Primitives (`AppButton`, `AppInput`, `AppModal`, …). Extend these before adding a new kit component |
| `ui/template/` | List/detail page templates, `PageHeader`, actions and their composables |
| `ui/shadcn/` | Local shadcn primitives built on Reka UI; consumed through App components |
| `ui/app/<cluster>/` | A primitive that needs several files (`select`, `date-picker`, `filters`) |
| `composables/` | App-wide composables (`useSession`, `useActionState`, `useToast`, `useWebSocketService`) |
| `utils/` | Small frontend helpers |
| `lib/` | Class-name composition (`cn`) for shadcn primitives; explicitly tracked despite Python `lib/` ignore rules |
| `components/` | App chrome that is not a generic primitive (layout header, drawer) |
| `stores/` | Rare app-level stores (`useSetupStore`: the selected organization) |

Auth lives in FastAPI: it sets and rotates HttpOnly cookies, the frontend never holds a token. The browser reaches the API on its own origin; during SSR Nitro calls `NUXT_API_INTERNAL_URL` with the request's cookie (GET only). There is no Nitro API proxy.

---

## Request flow (mental model)

```
Page (pages/) → Feature view → AppListTemplate / AppDetailTemplate (:resource)
              → Pinia Colada query/mutation ([key, 'list', params] / [key, id])
              → generated SDK function (organizationsList) → $api client
                  browser: /api/v1/… same origin (+cookies, Organization-Key, 401 → refresh → retry)
                  SSR:     NUXT_API_INTERNAL_URL/api/v1/… (+forwarded cookie)
                                                      ↓
Router (domains/*/views.py) → ViewSet → FilterObjectsManager → Model
                                         optional DomainService
```

Frontend never calls `useFetch`/`$fetch` for business resources — always a resource descriptor (or a generated SDK function with `useApiClient()` for non-CRUD actions).

In production every request enters the container through Caddy (`:8080`): `/api/v1/*` and `/ws/*` go to uvicorn on `127.0.0.1:8000`, `/_nuxt/*` is served from the build output, everything else goes to the Nuxt server on `127.0.0.1:3000`. In development `nuxt dev` (`:9001`) proxies `/api/v1/**` and `/ws/**` to uvicorn (`:9000`), so cookies and the CSRF Origin check behave the same. Details: [deployment.md](deployment.md).

---

## Infrastructure tree

```
Dockerfile                # One multi-stage image (backend venv, Nuxt build, runtime with s6-overlay)
.dockerignore             # Allowlist of the build context
Caddyfile                 # Reverse proxy inside the image
docker/rootfs/            # Copied to / in the image
  etc/s6-overlay/s6-rc.d/ #   one directory per service (migrate, backend, taskiq-*, frontend, caddy)
  etc/s6-overlay/scripts/ #   migrate, wait-for-db.py, service-finish (halts the container on a crash)
  usr/local/bin/healthcheck
compose.yaml              # Production stack: app + PostgreSQL + Redis
compose.override.yaml     # Local development only: db/redis ports on 127.0.0.1, app build
cliff.toml                # Release rules: next version and CHANGELOG.md from conventional commits
version.json              # Current release version (written by the release job, with pyproject/package.json)
.github/workflows/        # ci.yaml (checks → release → publish → deploy), rollback, pr-title, security
.github/actions/deploy/   # Pluggable deploy step (SSH + docker compose by digest)
```

Where new infrastructure goes:

- A new long-running process in the image → a new `s6-rc.d/<name>/` longrun (`type`, `run`, `finish` calling `service-finish`, `dependencies.d/migrate`) plus an entry in `user-bundles.d/user/contents.d/`.
- A new public route prefix for the backend → a `handle` block in `Caddyfile` before the Nuxt catch-all.
- A new runtime setting → `.env.example` and, if production-specific, the environment table in [deployment.md](deployment.md).
- A new CI check → a `make` target first (the Makefile is the source of truth), then a step in `ci.yaml`; add the job to the `gate` needs.

`AppListToolbar` is the shared search/filter composition: fixed in page list controls, sticky in nested lists. `UserProfileView` owns profile presentation; `pages/settings/profile.vue` only mounts the view.

---

## Agent tooling

The template is the seed of products that agents extend; this tooling keeps that fast and deterministic.

```
AGENTS.md, CLAUDE.md      # Agent index: Codex reads AGENTS.md, CLAUDE.md includes it for Claude Code
.agents/
  skills/<name>/SKILL.md  # Canonical skills for Claude Code and Codex: new-domain, design-system, sync-template
.claude/
  skills/<name>           # Relative symlinks -> ../../.agents/skills/<name> (Claude Code discovery path)
  settings.json           # Claude Code hooks (committed); personal overrides in settings.local.json (ignored)
  hooks/                  # block_migrations.py (PreToolUse Bash), format_file.py (PostToolUse Edit|Write)
scripts/
  scaffold/               # make new-domain: new_domain.py + templates/*.tmpl (string.Template)
  bootstrap/              # make init: init.py + product.md.tmpl
  tests/                  # Tests for the scaffolder, init and hooks (part of make check-backend)
.template-version         # Template version/commit a product is synced to
.vscode/                  # extensions.json + settings.json.example (Oxc, Ruff, Vue-only ESLint)
```

| Piece | Behavior |
|---|---|
| Domain discovery | `backend/app/core/discovery.py`: no registration step for models or routers ([backend-concept.md](backend-concept.md#registration)) |
| `make new-domain` | Scaffolds backend domain + frontend feature + drawer entry; never overwrites, never migrates ([backend-concept.md](backend-concept.md#scaffolding)) |
| `make init` | Turns a template copy into a product ([README.md](../README.md#start-a-new-product)) |
| Migration hook (Claude Code) | Blocks `make m/mm/migrate/make-migrations` and `tortoise migrate/makemigrations/upgrade/downgrade` with a message to ask the user. `ALLOW_MIGRATIONS=1 <command>` passes, only after the user explicitly asked |
| Format hook (Claude Code) | Formats only the edited file: Ruff for `backend/**/*.py`, `vp fmt` for `frontend/**`; no-op elsewhere; reports formatter problems as a note and never fails the edit |
| Skills | Short checklists that link to these docs; they do not copy rules. One copy in `.agents/skills/` ([Agent Skills](https://agentskills.io/specification) format: `name` = folder name, `description`, no tool-specific fields), read natively by Codex; Claude Code reads `.claude/skills/`, where each skill is a relative symlink to it. `new-domain` ends with a backend self-review; `design-system` covers new shadcn primitives and the browser review. Checking (`make check`) and releasing (commit types) are always-on rules in `AGENTS.md`, not skills |
| Forks | [template-ownership.md](template-ownership.md), `.template-version`, the `sync-template` skill |

Where new things go: a recurring agent workflow → `.agents/skills/<name>/SKILL.md`, its symlink (`ln -s ../../.agents/skills/<name> .claude/skills/<name>`) and a row in `AGENTS.md` — `scripts/tests/test_agent_skills.py` checks the pair and the frontmatter; a rule for every change belongs in `AGENTS.md`, not in a skill. On Windows the symlinks need Developer Mode + `git config --global core.symlinks true` before cloning (or WSL); otherwise they check out as plain text files and only Codex sees the skills; hooks stay small Python 3.9+ stdlib scripts reading the hook JSON on stdin, with tests in `scripts/tests/`. A change to a file that `make init` or `make new-domain` rewrites (Makefile image line, `app.config.ts`, the organization templates, `navigation/settings.ts`) must keep their patterns — `scripts/tests` fails when one goes missing.
