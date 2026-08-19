# FastAPI + Nuxt Production Template

Full-stack starter for internal apps with multi-organization access: CRUD entities, authentication, drawer navigation, and UI primitives for lists and forms.

What the template can do today (purpose, scenarios): [docs/product.md](docs/product.md).

## Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, PrimeVue, Tailwind CSS |
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
