# FastAPI + Nuxt Production Template

Full-stack starter for internal apps with multi-organization access: CRUD entities, authentication, drawer navigation, and UI primitives for lists and forms.

What the template can do today (purpose, scenarios): [docs/product.md](docs/product.md).

## Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, shadcn-vue / Reka UI, Tailwind CSS |
| Infra | One Docker image (s6-overlay: Caddy, uvicorn, Nuxt, Taskiq), Docker Compose, GitHub Actions, Makefile |

The backend exposes a REST API (`/api/v1`); the frontend is a Nuxt 4 app (server-side rendered today; hybrid rendering is planned in [docs/roadmap.md](docs/roadmap.md)) with a repo layer on top of `$api`. Data is scoped by user and current organization.

Structure, folder roles, and how to add a domain or feature: [docs/architecture.md](docs/architecture.md), [docs/backend-concept.md](docs/backend-concept.md), [docs/frontend-concept.md](docs/frontend-concept.md). Agent index: [AGENTS.md](AGENTS.md).

---

## Quick start

### 1. Environment

Requirements: Python 3.14 (`.python-version`) with [uv](https://docs.astral.sh/uv/), Node 24 (`.nvmrc`; `^22.18 || ^24.11` supported) and pnpm from `packageManager` in `frontend/package.json` (`corepack enable`).

```bash
cp .env.example .env
make install                 # uv sync + pnpm install
docker compose up -d db redis  # PostgreSQL + Redis on 127.0.0.1 (compose.override.yaml), not the `app` container
make m                       # apply migrations
```

Ports come from `.env` (`BACKEND_PORT`, `FRONTEND_PORT`); the defaults in `.env.example`, the Makefile and `nuxt.config.ts` are **9000** (API) and **9001** (Nuxt), and the backend CORS default allows the Nuxt origin. `NUXT_PUBLIC_BASE_URL` must point at the API. The Makefile reads only the keys it needs from `.env` and works without the file.

Public registration is off. Create the first user:

```bash
cd backend && python -m manage create_superuser
```

### 2. Run

In two terminals:

```bash
make rb   # backend → http://localhost:9000  (OpenAPI: /docs)
make rf   # frontend → http://localhost:9001
```

Sign in, then pick or create an organization on the setup screen. After that, Home and Settings work in that org.

For background tasks (optional; no product jobs are defined yet):

```bash
make rt   # Taskiq scheduler + worker
```

Other useful commands: `make mm` (create migrations), `make help`.

---

## Makefile

| Command | Action |
|---|---|
| `make install` | Install backend + frontend dependencies |
| `make mm` | Create migrations (tortoise makemigrations) |
| `make m` | Apply migrations |
| `make rb` | Run backend (uvicorn, reload) |
| `make rf` | Run frontend (nuxt dev) |
| `make rt` | Run Taskiq scheduler + worker |
| `make lint` | Fix and format: `ruff check --fix` + `ruff format`; `pnpm fmt` + `pnpm lint:fix` |
| `make fmt` | Format only (ruff format, Oxfmt) |
| `make check` | Everything CI checks, read-only: `check-backend` + `check-frontend` |
| `make check-backend` | `ruff check`, `ruff format --check`, `ty check`, pytest (`PYTEST_ARGS`, default `--keepdb`; `PYTEST_ARGS=--sqlite` without Postgres) |
| `make check-frontend` | `pnpm check` (format check, Oxlint + ESLint for Vue templates, typecheck, Vitest, architecture guard); `BUILD=1` adds `nuxt build` |
| `make openapi` | Write the OpenAPI schema to `frontend/openapi.json` (no database needed); commit it with API changes |
| `make test` / `make t` | Run backend tests (pytest, same `PYTEST_ARGS`) |
| `make docker-build` | Build the production image (`IMAGE`, default `fastapi-nuxt-template:local`; version from `version.json`) |
| `make docker-run` | Run `IMAGE` with PostgreSQL + Redis from `compose.yaml` (project `<COMPOSE_PROJECT_NAME>-smoke`) and wait until healthy |
| `make docker-stop` | Stop the `docker-run` stack and delete its volumes |

## UI catalogue and frontend checks

Open `http://localhost:9001/ui` (or your configured frontend port) to inspect the public catalogue with local sample data. App components use shadcn/Reka primitives, shared control sizes, semantic light/dark tokens, and `Modal` naming. Screen composition and repo/codec patterns are documented in [docs/frontend-concept.md](docs/frontend-concept.md).

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
