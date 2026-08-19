# Architecture

Full-stack template: FastAPI REST API (`/api/v1`) + Nuxt SPA. Data is scoped by the current user and organization (`FilterObjectsManager` on the backend, `Organization-Key` on the frontend).

What the app does (purpose, scenarios): [product.md](product.md).

| Layer | Stack |
|---|---|
| Backend | Python 3.14, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, PrimeVue, Tailwind CSS |
| Infra | Docker Compose, Caddy (prod), Makefile |

**Where to put new code**

- Business capability (CRUD entity, org, user) → a **domain** on the backend and a **feature** on the frontend. Same name when possible (`organization` / `organization`).
- Cross-cutting infrastructure (auth kernel, S3, base viewset) → `backend/app/core/` or `frontend/app/shared/`.
- Pages are thin: they only mount a feature view. Layouts own navigation.

Canonical examples: `backend/app/domains/organization/`, `frontend/app/features/organization/`. Live UI primitives: `/home/ui`.

### New capability — definition of done

Same change, all of this (skip a row only if it does not apply):

| Layer | Done when |
|---|---|
| Backend | Domain files (`models`, `schemas`, `filters`, `views`). Register in `core/database.py` (`MODELS`), `main.py` (`include_router`), **`FilterObjectsManager`**. Views stay thin — workflows in a **service** (instances in, not ids). See [backend-concept.md](backend-concept.md#services-vs-viewsets-vs-utils) |
| Tests | Non-trivial rules get pytest next to the domain (`domains/<name>/tests/`). See [backend-concept.md](backend-concept.md#tests). Canonical: `domains/organization/tests/test_organization.py` |
| Frontend | Feature: model + codec, repo, `useRepo` registry, views on `AppListTemplate` / `AppDetailTemplate`, thin page, drawer item if needed. User-facing copy in **Russian** |
| Realtime | Org events go through **`OrganizationWebSocketService`**, not a new websocket stack |
| Docs | [product.md](product.md) if the user can see or do something new. Concept docs if the pattern itself changed |
| Lint | `make lint` is green |
| Migration | Tell the user `make mm` / `make m` is needed. Do not run it unless they ask |

---

## Backend tree

```
backend/app/
  main.py                 # FastAPI app: middleware, /api/v1 routers, /ws, /health
  conftest.py             # Shared pytest fixtures (in-memory Tortoise `db`)
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
| `database.py` | Tortoise `MODELS` list and ORM setup. **Register every new domain models module here.** |
| `auth.py` | Current user / org (`AuthState`) |
| `viewsets.py` | `BaseModelViewSet` / `BaseReadOnlyViewSet` — auth, pagination, scoping |
| `models.py` | `BaseModel` (`id`, `created_at`, `updated_at`) and base schemas |
| `broker.py` | Taskiq |
| `exceptions.py` | Exception handlers |
| `services/` | Infrastructure **classes** (S3, crypto, logger, websocket) |
| `utils/` | Small **functions** (dates, exception details, M2M helpers) |
| `fields/` | Reusable Tortoise/Pydantic fields |
| `tests/` | App-level tests (health, auth smoke) — not domain tests |

### `domains/<name>/` — business module

One domain can contain several models. Split files by role, not by putting everything in `views.py`.

| Path | Why it exists |
|---|---|
| `models.py` | Tortoise models for this domain |
| `schemas.py` | Create / update / read DTOs (`@schema(model=…)`) |
| `filters.py` | fastapi-ronin `FilterSet` (list search/filter) |
| `views.py` | Routers + viewsets (HTTP). Keep this thin — call services for non-CRUD logic |
| `services/` | Domain **classes** (see services vs utils below) |
| `tests/` | Tests for this domain: `tests/test_<subject>.py` |

Register the domain: `core/database.py` (`MODELS`) + `main.py` (`include_router`) + `shared/services/filter_objects_manager.py` (queryset scope).

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
frontend/app/
  features/               # One folder per business module (mirrors a backend domain)
  pages/                  # Nuxt routes — thin wrappers over feature views
  layouts/                # Shell + drawer navigation (default, settings, setup, auth)
  shared/                 # UI kit, repo toolkit, composables, utils
  middleware/             # Auth / setup redirects
  plugins/                # `$api` and other app plugins
```

### `features/<name>/`

| Path | Why it exists |
|---|---|
| `models/` | One **entity per file**: TypeScript type + `createCodec` (decode API → model, encode model → payload). `organization.ts` and `organizationUser.ts` stay separate |
| `repos/` | Pinia store around `createAppRepo`. `resource` matches the backend URL prefix. Register in `shared/composables/useRepo.ts` |
| `views/` | Screen-level UI: list page, detail page, or a large section used as a page. Built on `AppListTemplate` / `AppDetailTemplate` |
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

Same idea already exists in the UI kit: `shared/ui/app/smartDatePicker/` (components + local composables).

### `pages/` and `layouts/`

| Path | Why it exists |
|---|---|
| `pages/**/*.vue` | Route only. Import a feature view; no business logic, no repo calls |
| `layouts/*.vue` | Chrome and **drawer items**. Nuxt route names come from the file path: `settings/organizations/[id].vue` → `settings-organizations-id` |

### `shared/`

| Path | Why it exists |
|---|---|
| `ui/app/` | Primitives (`AppButton`, `AppInput`, `AppModal`, …). Extend these before adding a new kit component |
| `ui/template/` | List/detail page templates and their composables |
| `ui/app/<cluster>/` | A primitive that needs several files (see `smartDatePicker`) |
| `composables/` | App-wide composables (`useRepo`, `useActionState`, `useNotify`) |
| `toolkits/repo/` | Generic repo/codec/pagination — do not fork this per feature |
| `toolkits/authentication/` | Token storage and auth client |
| `utils/` | Small frontend helpers |
| `components/` | App chrome that is not a generic primitive (layout header, drawer) |
| `stores/` | Rare app-level stores (setup wizard) |

---

## Request flow (mental model)

```
Page (pages/) → Feature view → useRepo('key') → $api /api/v1/…
                                                      ↓
Router (domains/*/views.py) → ViewSet → FilterObjectsManager → Model
                                         optional DomainService
```

Frontend never calls `useFetch` for business resources — always a repo.
