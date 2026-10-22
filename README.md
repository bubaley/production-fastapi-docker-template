# FastAPI + Nuxt Production Template

Full-stack starter for internal apps with multi-organization access: CRUD entities, authentication, drawer navigation, and UI primitives for lists and forms. Built to be the seed of many products that AI agents (Claude Code) extend quickly and safely.

What every product inherits: [docs/template-core.md](docs/template-core.md). What this product does on top: [docs/product.md](docs/product.md).

## Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.15, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, shadcn-vue / Reka UI, Tailwind CSS |
| Infra | One Docker image (s6-overlay: Caddy, uvicorn, Nuxt, Taskiq), Docker Compose, GitHub Actions, Makefile |

The backend exposes a REST API (`/api/v1`) and owns auth (HttpOnly cookies); the frontend is a Nuxt 4 app with hybrid rendering (client-only app routes, SSR public pages) that calls the API through a client generated from the OpenAPI schema. Data is scoped by user and current organization.

Structure, folder roles, and how to add a domain or feature: [docs/architecture.md](docs/architecture.md), [docs/backend-concept.md](docs/backend-concept.md), [docs/frontend-concept.md](docs/frontend-concept.md). Agent index: [AGENTS.md](AGENTS.md).

---

## Start a new product

Create a repository from this template (GitHub "Use this template", or clone it), then:

```bash
make init name=field-service title="Выездной сервис"   # rename, .env with fresh secrets, versions 0.1.0, product.md skeleton
git add -A && git commit -m "chore: initialize from template"
make install                                          # uv sync + pnpm install
docker compose up -d db redis                         # PostgreSQL + Redis on 127.0.0.1
make m                                                # apply migrations (you run this; agents never do)
make createsuperuser                                  # first user
make run-backend                                      # terminal 1 → http://localhost:9000/docs
make run-frontend                                     # terminal 2 → http://localhost:9001
```

`make init` (`scripts/bootstrap/init.py`) renames the project everywhere it is greppable (compose project, database, package names, API title, UI name, image names), writes `.env` from `.env.example` with a fresh `SECRET_KEY` and `ENCRYPTION_KEY`, resets `version.json`/`CHANGELOG.md` and package versions to 0.1.0, replaces [docs/product.md](docs/product.md) with the product skeleton and records the template version in `.template-version`. It refuses a dirty tree (`force=1` overrides) and is safe to run again. If the copy kept the template's `v*` tags, delete them before the first push (it tells you how).

Then describe the product in `docs/product.md` (purpose, personas, scenarios, non-goals) — agents build only what is written there or in [docs/template-core.md](docs/template-core.md). To pull later template improvements into the product, run the `/sync-template` skill ([docs/template-ownership.md](docs/template-ownership.md)).

## Adding a domain

```bash
make new-domain name=invoice title="Счета" item_title="Счёт"
```

Generates an organization-scoped CRUD entity end to end — backend domain (model with `tenant_scope`, schemas, filters, thin viewset, tests) and frontend feature (resource descriptor, list and detail views, settings pages, drawer entry) — mirroring the canonical `organization` code. Models and routers are discovered automatically. Then fill in the real fields, run the migration (`make mm`, `make m`), `make gen-client`, `make check`, and update `docs/product.md`. Details: [docs/backend-concept.md](docs/backend-concept.md#scaffolding); agents follow the `/new-domain` skill.

## Agent tooling

[AGENTS.md](AGENTS.md) is the index agents read first (`CLAUDE.md` includes it). `.claude/` is committed: skills (`new-domain`, `verify`, `design-system`, `add-shadcn-component`, `sync-template`, `release`), review subagents (`domain-reviewer`, `ui-reviewer`) and hooks that block migration commands (prefix `ALLOW_MIGRATIONS=1` when you ask an agent to run one) and format every edited file. Editor setup: copy `.vscode/settings.json.example` to `.vscode/settings.json` and install the recommended extensions. Overview: [docs/architecture.md](docs/architecture.md#agent-tooling).

---

## Quick start (this repository)

### 1. Environment

Requirements: Python 3.15 (`.python-version`) with [uv](https://docs.astral.sh/uv/) 0.13+, Node 26 (`.nvmrc`) and pnpm 12 from `packageManager` in `frontend/package.json` (`npm install -g pnpm@12`; Node 26 no longer ships corepack).

```bash
cp .env.example .env
make install                 # uv sync + pnpm install
docker compose up -d db redis  # PostgreSQL + Redis on 127.0.0.1 (compose.override.yaml), not the `app` container
make m                       # apply migrations
```

Ports come from `.env` (`BACKEND_PORT`, `FRONTEND_PORT`); the defaults in `.env.example`, the Makefile and `nuxt.config.ts` are **9000** (API) and **9001** (Nuxt), and the backend CORS default allows the Nuxt origin. The browser always calls the API on the Nuxt origin: in development `nuxt dev` proxies `/api/v1/**` and `/ws/**` to the backend (`NUXT_API_INTERNAL_URL`, default `http://localhost:$BACKEND_PORT`), so the HttpOnly session cookies work as in production. The Makefile reads only the keys it needs from `.env` and works without the file.

Public registration is off. Create the first user:

```bash
make createsuperuser
```

### 2. Run

In two terminals:

```bash
make rb   # backend → http://localhost:9000  (OpenAPI: /docs)
make rf   # frontend → http://localhost:9001 (public page `/`, app at /home)
```

Open http://localhost:9001/auth, sign in, then pick or create an organization on the setup screen. After that, Home and Settings work in that org.

For background tasks (optional; no product jobs are defined yet):

```bash
make rt   # Taskiq scheduler + worker
```

Other useful commands: `make mm` (create migrations), `make help`.

---

## Makefile

| Command | Action |
|---|---|
| `make init name=<kebab-name> [title="…"]` | Turn a fresh template copy into a new product (see [Start a new product](#start-a-new-product)) |
| `make new-domain name=<snake_name> [title="…"] [item_title="…"]` | Scaffold a backend domain + frontend feature (see [Adding a domain](#adding-a-domain)) |
| `make install` | Install backend + frontend dependencies |
| `make createsuperuser` | Create the first user (interactive) |
| `make mm` | Create migrations (tortoise makemigrations) |
| `make m` | Apply migrations |
| `make rb` | Run backend (uvicorn, reload) |
| `make rf` | Run frontend (nuxt dev) |
| `make rt` | Run Taskiq scheduler + worker |
| `make lint` | Fix and format: `ruff check --fix` + `ruff format`; `pnpm fmt` + `pnpm lint:fix` |
| `make fmt` | Format only (ruff format, Oxfmt) |
| `make check` | Everything CI checks, read-only: `check-backend` + `check-frontend` |
| `make check-backend` | `ruff check`, `ruff format --check`, `ty check`, pytest (`PYTEST_ARGS`, default `--keepdb`; `PYTEST_ARGS=--sqlite` without Postgres), tooling tests (`scripts/tests`: scaffolder, init, hooks) |
| `make check-frontend` | `pnpm check` (format check, Oxlint + ESLint for Vue templates, typecheck, Vitest, architecture guard); `BUILD=1` adds `nuxt build` |
| `make openapi` | Write the OpenAPI schema to `frontend/openapi.json` (no database needed); commit it with API changes |
| `make gen-client` | `make openapi` + `pnpm gen:api`: regenerate the typed frontend client in `frontend/app/shared/api/generated/` (commit it; `pnpm check` fails when it is stale) |
| `make test` / `make t` | Run backend tests (pytest, same `PYTEST_ARGS`) |
| `make docker-build` | Build the production image (`IMAGE`, default `fastapi-nuxt-template:local`; version from `version.json`) |
| `make docker-run` | Run `IMAGE` with PostgreSQL + Redis from `compose.yaml` (project `<COMPOSE_PROJECT_NAME>-smoke`) and wait until healthy |
| `make docker-stop` | Stop the `docker-run` stack and delete its volumes |

## UI catalogue and frontend checks

Open `http://localhost:9001/ui` (or your configured frontend port) to inspect the public catalogue with local sample data. App components use shadcn/Reka primitives, shared control sizes, semantic light/dark tokens, and `Modal` naming. Screen composition and resource descriptors are documented in [docs/frontend-concept.md](docs/frontend-concept.md).

Frontend scripts (from `frontend/`; tooling details in [docs/frontend-concept.md](docs/frontend-concept.md#tooling)):

```bash
pnpm fmt            # Oxfmt (Vite+), incl. Tailwind class order
pnpm lint           # Oxlint + ESLint for *.vue templates (lint:fix to fix)
pnpm test           # Vitest via vp test
pnpm typecheck      # nuxt typecheck (vue-tsc)
pnpm check          # all of the above + architecture guard, as in CI
pnpm check:unused   # knip: unused files and dependencies (also part of check)
pnpm build          # production build
```

Run `make lint` (fix) and `make check` (verify) from the repository root. For UI changes, also inspect `/ui` and affected screens in a browser — see the checklist in [docs/frontend-concept.md](docs/frontend-concept.md#ui-layers-and-visual-review). Passing automated checks does not substitute for that visual review.

## Production image, CI and releases

Production runs one image: Caddy on `:8080` in front of FastAPI and Nuxt, plus the Taskiq worker and scheduler, supervised by s6-overlay. The container applies migrations on start and exits if any service dies. `compose.yaml` is the production stack (app + PostgreSQL + Redis); `compose.override.yaml` only adds local-development ports and the build. Try the image locally with `make docker-build && make docker-run` (needs `.env`).

`.github/workflows/ci.yaml` is the only pipeline. Pull requests run the backend checks (PostgreSQL + Redis), frontend checks with the production build, repository hygiene, and an image build with a compose smoke test and a Trivy scan — each only when its paths change. **CI gate** is the single required check. On `main`, after the gate passes, the pipeline computes the next version from conventional commits (`feat` → minor; `fix`, `perf`, `build`, `chore(deps)` → patch; `!` → major), commits `chore(release): vX.Y.Z [skip ci]` with `CHANGELOG.md`, tags it, publishes the image to Yandex Container Registry and deploys it by digest. Publishing and deploying stay off until their repository variables are set; PR titles must be conventional because they become the squash commit.

Image layout, services, health endpoints, release rules, rollback, and the secrets and variables to configure: [docs/deployment.md](docs/deployment.md).
