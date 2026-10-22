# FastAPI + Nuxt Production Template

Full-stack starter for internal apps with multi-organization access: CRUD entities, authentication, drawer navigation, and UI primitives for lists and forms.

What the template can do today (purpose, scenarios): [docs/product.md](docs/product.md).

## Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, shadcn-vue / Reka UI, Tailwind CSS |
| Infra | Docker Compose, Caddy (prod), Makefile |

The backend exposes a REST API (`/api/v1`); the frontend is a Nuxt 4 app (server-side rendered today; hybrid rendering is planned in [docs/roadmap.md](docs/roadmap.md)) with a repo layer on top of `$api`. Data is scoped by user and current organization.

Structure, folder roles, and how to add a domain or feature: [docs/architecture.md](docs/architecture.md), [docs/backend-concept.md](docs/backend-concept.md), [docs/frontend-concept.md](docs/frontend-concept.md). Agent index: [AGENTS.md](AGENTS.md).

---

## Quick start

### 1. Environment

Requirements: Python 3.14 (`.python-version`) with [uv](https://docs.astral.sh/uv/), Node 24 (`.nvmrc`; `^22.18 || ^24.11` supported) and pnpm from `packageManager` in `frontend/package.json` (`corepack enable`).

```bash
cp .env.example .env
make install                 # uv sync + pnpm install
docker compose up -d db redis  # PostgreSQL + Redis only (not the prod `app` container)
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
| `make test` / `make t` | Run backend tests (pytest, same `PYTEST_ARGS`) |

## UI catalogue and frontend checks

Open `http://localhost:9001/ui` (or your configured frontend port) to inspect the public catalogue with local sample data. App components use shadcn/Reka primitives, shared control sizes, semantic light/dark tokens, and `Modal` naming. Screen composition and repo/codec patterns are documented in [docs/frontend-concept.md](docs/frontend-concept.md).

Frontend scripts (from `frontend/`; tooling details in [docs/frontend-concept.md](docs/frontend-concept.md#tooling)):

```bash
pnpm fmt            # Oxfmt (Vite+), incl. Tailwind class order
pnpm lint           # Oxlint + ESLint for *.vue templates (lint:fix to fix)
pnpm test           # Vitest via vp test
pnpm typecheck      # nuxt typecheck (vue-tsc)
pnpm check          # all of the above + architecture guard, as in CI
pnpm check:unused   # knip: unused files and dependencies (not part of check)
pnpm build          # production build
```

Run `make lint` (fix) and `make check` (verify) from the repository root. For UI changes, also inspect `/ui` and affected screens in a browser — see the checklist in [docs/frontend-concept.md](docs/frontend-concept.md#ui-layers-and-visual-review). Passing automated checks does not substitute for that visual review.

## CI and releases

CI checks backend lint and tests, plus frontend `pnpm check` (format, Oxlint/ESLint, TypeScript, Vitest, architecture guard) and production build with locked dependencies. `All Checks Passed` requires every backend and frontend job to succeed. A successful `push` run on `main` starts the release workflow: `prepare` generates the version/tag and changelog from the exact tested commit, `docker` gates the final build, and `release` publishes the GitHub Release only after both jobs succeed. A failed or skipped build prevents publication. Release runs are serialized; a stale CI commit cannot prepare a release after `main` has advanced.

The Docker build steps are intentionally commented out in this template. The active `docker` job contains a placeholder, so template releases require no container registry credentials. For a real project, set `IMAGE_NAME` in the workflow and repository secrets `YC_REGISTRY` and `YC_KEY_JSON`; replace the placeholder by uncommenting the steps inside `docker`. Keep `release.needs: [prepare, docker]`. The build checks out the generated tag, builds the final runtime image and pushes its version and `latest` tags before release publication. Deployment is not configured here.

The version commit and Git tag are prepared before the build. If a production build fails, rerun its failed jobs after fixing the cause; do not restart the whole workflow to generate a second version. GitHub Release publication remains the last step.
