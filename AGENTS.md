# Agent instructions

This file is an index. Do not copy patterns here — follow the linked docs.

## How to look things up

| Question | Where |
|---|---|
| What does the product do? Which scenarios exist? | [docs/product.md](docs/product.md) (product-owned) on top of [docs/template-core.md](docs/template-core.md) (inherited capabilities). `product.md` wins on conflict |
| Start a new product from the template | `make init name=<kebab-name> title="…"` — [README.md](README.md#start-a-new-product) |
| Add a domain (backend + frontend CRUD)? | `make new-domain name=<snake_name> title="…"`, then the `/new-domain` skill — [docs/backend-concept.md](docs/backend-concept.md#scaffolding) |
| Which files does the template own in a fork? How to pull template updates? | [docs/template-ownership.md](docs/template-ownership.md), `.template-version`, the `/sync-template` skill |
| Which skills, subagents and hooks exist? | `.claude/skills/*/SKILL.md` (`new-domain`, `verify`, `design-system`, `add-shadcn-component`, `sync-template`, `release`), `.claude/agents/` (`domain-reviewer`, `ui-reviewer`), hooks in `.claude/settings.json` — [docs/architecture.md](docs/architecture.md#agent-tooling) |
| How does existing code work, who calls X, what depends on Y? | MCP **codebase-memory** first (`search_graph`, `get_architecture`, `trace_path`, `get_code_snippet`). Then open the files it points to. |
| Where does a new file go? What is each folder for? | [docs/architecture.md](docs/architecture.md) |
| How to add a backend domain, model, viewset, service? | [docs/backend-concept.md](docs/backend-concept.md) — canonical code: `backend/app/domains/organization/` |
| How to add a frontend feature, resource descriptor, view? | [docs/frontend-concept.md](docs/frontend-concept.md) — canonical code: `frontend/app/features/organization/` |
| How does the frontend call the API (generated client, query keys, session, SSR pages)? After an API change? | [docs/frontend-concept.md](docs/frontend-concept.md#data-layer) — `make gen-client` regenerates the client |
| Auth contract (cookies, CSRF, SSR), OpenAPI conventions, `make openapi`? | [docs/backend-concept.md](docs/backend-concept.md#auth-and-tokens) and [#openapi-contract](docs/backend-concept.md#openapi-contract) |
| When to write backend tests, where they live? | [docs/backend-concept.md](docs/backend-concept.md#tests) — canonical: `backend/app/domains/organization/tests/test_organization.py` |
| How to run the project locally? | [README.md](README.md) |
| How is the image built, released and deployed? | [docs/deployment.md](docs/deployment.md) — `Dockerfile`, `docker/rootfs/`, `.github/workflows/ci.yaml` |
| How to lint, format, test, what CI checks? | `make lint` / `make check` in [README.md](README.md#makefile); frontend tooling in [docs/frontend-concept.md](docs/frontend-concept.md#tooling) |
| What is being modernized right now, and which decisions are fixed? | [docs/roadmap.md](docs/roadmap.md) |

If the knowledge graph is missing or stale, index the repo with codebase-memory. Do not invent architecture from memory. Do not invent capabilities that are in neither [docs/template-core.md](docs/template-core.md) nor [docs/product.md](docs/product.md); when they disagree, `product.md` wins.

## Always-on rules

- **Do not run migrations** (`make mm`, `make m`, Tortoise migrate) unless the user explicitly asks. After model changes, describe the migration needed. A hook blocks these commands; when the user explicitly asked, prefix the command with `ALLOW_MIGRATIONS=1`.
- **Do not duplicate.** Extend existing viewsets, UI primitives, repos, and helpers before creating new ones.
- Comments in code: English only, and only when the logic is non-obvious.
- User-facing UI copy is **Russian**. Do not add English labels, titles, or toasts in product screens. The one exception is the `/ui` component catalogue: its section titles and sample content are English so they read alongside the prop names they demonstrate.
- After a non-trivial change, run **`make lint`** (fixes and formats both sides), then **`make check`** (what CI runs: format check, lint, types, tests, architecture guard; read-only). Fix what `make check` reports — do not leave it red. Without local Postgres: `make check PYTEST_ARGS=--sqlite`.
- Complex backend behavior needs tests — see [docs/backend-concept.md](docs/backend-concept.md#tests). Canonical: `backend/app/domains/organization/tests/test_organization.py`.

## Keep docs current

A change is incomplete if the matching doc still describes the old product or pattern. Update docs in the **same** change — do not defer.

| What changed | Update |
|---|---|
| User-facing behavior or scenario | [docs/product.md](docs/product.md); an inherited capability of every product (template repo only) → [docs/template-core.md](docs/template-core.md) |
| A new template path, or who owns a path in forks | [docs/template-ownership.md](docs/template-ownership.md) |
| How a skill, subagent or hook works | its file under `.claude/`; the overview in [docs/architecture.md](docs/architecture.md#agent-tooling) |
| Folder roles, request flow, where new files go | [docs/architecture.md](docs/architecture.md) |
| How to add/grow a backend domain (model, schema, viewset, scope, tests) | [docs/backend-concept.md](docs/backend-concept.md) |
| How to add/grow a frontend feature (resource descriptor, view, templates, data layer) | [docs/frontend-concept.md](docs/frontend-concept.md) |
| How to run, ports, first user, Makefile | [README.md](README.md) |
| New recurring pattern not covered above | New `docs/<topic>.md` **and** a row in the lookup table in this file |

When you add a backend domain + frontend feature, follow the definition of done in [docs/architecture.md](docs/architecture.md) and update **product.md** if the user can see or do something new. If the knowledge graph would be wrong after a large structural change, re-index codebase-memory.

## Extending these docs

A new recurring pattern → add `docs/<topic>.md` and one row to the lookup table above. Do not paste the pattern back into this file.
