# Agent instructions

This file is an index. Do not copy patterns here — follow the linked docs.

## How to look things up

| Question | Where |
|---|---|
| What does the product do? Which scenarios exist? | [docs/product.md](docs/product.md) |
| How does existing code work, who calls X, what depends on Y? | MCP **codebase-memory** first (`search_graph`, `get_architecture`, `trace_path`, `get_code_snippet`). Then open the files it points to. |
| Where does a new file go? What is each folder for? | [docs/architecture.md](docs/architecture.md) |
| How to add a backend domain, model, viewset, service? | [docs/backend-concept.md](docs/backend-concept.md) — canonical code: `backend/app/domains/organization/` |
| How to add a frontend feature, model, repo, view? | [docs/frontend-concept.md](docs/frontend-concept.md) — canonical code: `frontend/app/features/organization/` |
| When to write backend tests, where they live? | [docs/backend-concept.md](docs/backend-concept.md#tests) — canonical: `backend/app/domains/organization/tests/test_organization.py` |
| How to run the project locally? | [README.md](README.md) |

If the knowledge graph is missing or stale, index the repo with codebase-memory. Do not invent architecture from memory. Do not invent product capabilities that are not in [docs/product.md](docs/product.md).

## Always-on rules

- **Do not run migrations** (`make mm`, `make m`, Tortoise migrate) unless the user explicitly asks. After model changes, describe the migration needed.
- **Do not duplicate.** Extend existing viewsets, UI primitives, repos, and helpers before creating new ones.
- Comments in code: English only, and only when the logic is non-obvious.
- User-facing UI copy is **Russian**. Do not add English labels, titles, or toasts in product screens.
- After a non-trivial change, run **`make lint`** and fix what it reports. Do not leave a red linter.
- Complex backend behavior needs tests — see [docs/backend-concept.md](docs/backend-concept.md#tests). Canonical: `backend/app/domains/organization/tests/test_organization.py`.

## Keep docs current

A change is incomplete if the matching doc still describes the old product or pattern. Update docs in the **same** change — do not defer.

| What changed | Update |
|---|---|
| User-facing behavior or scenario | [docs/product.md](docs/product.md) |
| Folder roles, request flow, where new files go | [docs/architecture.md](docs/architecture.md) |
| How to add/grow a backend domain (model, schema, viewset, scope, tests) | [docs/backend-concept.md](docs/backend-concept.md) |
| How to add/grow a frontend feature (model, repo, view, templates) | [docs/frontend-concept.md](docs/frontend-concept.md) |
| How to run, ports, first user, Makefile | [README.md](README.md) |
| New recurring pattern not covered above | New `docs/<topic>.md` **and** a row in the lookup table in this file |

When you add a backend domain + frontend feature, follow the definition of done in [docs/architecture.md](docs/architecture.md) and update **product.md** if the user can see or do something new. If the knowledge graph would be wrong after a large structural change, re-index codebase-memory.

## Extending these docs

A new recurring pattern → add `docs/<topic>.md` and one row to the lookup table above. Do not paste the pattern back into this file.
