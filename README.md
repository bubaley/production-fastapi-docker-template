# FastAPI + Nuxt Production Template

Full-stack starter for internal apps with multi-organization access: CRUD entities, authentication, drawer navigation, and UI primitives for lists and forms.

What the template can do today (purpose, scenarios): [docs/product.md](docs/product.md).

## Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, shadcn-vue / Reka UI, Tailwind CSS |
| Infra | Docker Compose, Caddy (prod), Makefile |

The backend exposes a REST API (`/api/v1`); the frontend is an SPA with a repo layer on top of `$api`. Data is scoped by user and current organization.

Structure, folder roles, and how to add a domain or feature: [docs/architecture.md](docs/architecture.md), [docs/backend-concept.md](docs/backend-concept.md), [docs/frontend-concept.md](docs/frontend-concept.md). Agent index: [AGENTS.md](AGENTS.md).

---

## Quick start

### 1. Environment

```bash
cp .env.example .env
make install                 # uv sync + pnpm install
docker compose up -d db redis  # PostgreSQL + Redis only (not the prod `app` container)
make m                       # apply migrations
```

Ports come from `.env` (`BACKEND_PORT`, `FRONTEND_PORT`). `.env.example` uses **9000** (API) and **9001** (Nuxt). `NUXT_PUBLIC_BASE_URL` must point at the API.

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
| `make lint` | Backend pre-commit (ruff, …) + frontend ESLint |
| `make test` / `make t` | Run backend tests (pytest) |

## UI catalogue and frontend checks

Open `http://localhost:9001/ui` (or your configured frontend port) to inspect the public catalogue with local sample data. `/home/ui` redirects to `/ui`. App components use shadcn/Reka primitives, Tasker control sizes, semantic light/dark tokens, and `Modal` naming. Screen composition and repo/codec patterns are documented in [docs/frontend-concept.md](docs/frontend-concept.md).

Run frontend checks from `frontend/`:

```bash
pnpm test           # Vitest: repo/query and UI behavior
pnpm typecheck      # Nuxt + Vue TypeScript checks
pnpm build         # production build
```

Run `make lint` from the repository root. For UI changes, also inspect `/ui` and affected screens in a browser, including mobile width, both themes, empty/loading/error states and nested overlays. Passing automated checks does not substitute for that visual review.

## CI and releases

CI checks backend lint and tests, plus frontend ESLint, TypeScript, Vitest and production build with locked dependencies. `All Checks Passed` requires every backend and frontend job to succeed. A successful `push` run on `main` starts the release workflow: `prepare` generates the version/tag and changelog from the exact tested commit, `docker` gates the final build, and `release` publishes the GitHub Release only after both jobs succeed. A failed or skipped build prevents publication. Release runs are serialized; a stale CI commit cannot prepare a release after `main` has advanced.

The Docker build steps are intentionally commented out in this template. The active `docker` job contains a placeholder, so template releases require no container registry credentials. For a real project, set `IMAGE_NAME` in the workflow and repository secrets `YC_REGISTRY` and `YC_KEY_JSON`; replace the placeholder by uncommenting the steps inside `docker`. Keep `release.needs: [prepare, docker]`. The build checks out the generated tag, builds the final runtime image and pushes its version and `latest` tags before release publication. Deployment is not configured here.

The version commit and Git tag are prepared before the build. If a production build fails, rerun its failed jobs after fixing the cause; do not restart the whole workflow to generate a second version. GitHub Release publication remains the last step.
