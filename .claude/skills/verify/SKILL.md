---
name: verify
description: Run and interpret the project's full check suite (make check) for this FastAPI + Nuxt template. Use before declaring any change done, before committing, when CI is red, or when the user asks to verify, test, lint or check the project.
---

# Verify

`make check` is exactly what CI runs (read-only). Source of truth: the `check*` targets in the [Makefile](../../../Makefile).

1. Fix-and-format first: `make lint` (ruff fix/format for backend + tooling, Oxfmt + Oxlint/ESLint fix for frontend).
2. Run `make check`. Postgres down (`docker compose up -d db` fails or tests cannot connect) or the change has an unapplied migration → `make check PYTEST_ARGS=--sqlite`. Say which mode you used.
3. Read the first failure, not the last line. Map it:
   | Failure | Meaning / fix |
   |---|---|
   | `ruff check` / `ruff format --check` | Run `make lint`; remaining errors are real (fix code, do not add `noqa` without a reason) |
   | `ty check` | Type error in backend code |
   | pytest `frontend/openapi.json is stale` | API changed: `make gen-client` and commit `openapi.json` + `generated/` |
   | pytest `DomainDiscoveryError` | A domain's `views.py` failed to import or exports no `routers` |
   | pytest `ScopeConfigurationError` | A model lacks `tenant_scope` ([backend-concept.md](../../../docs/backend-concept.md#scoping)) |
   | pytest relation/table missing (Postgres only) | Migration not applied: ask the user to run `make m`, use `--sqlite` meanwhile |
   | `scripts/tests` | Scaffolder, `make init` or `.claude/hooks` broke; a template file they rewrite may have changed shape |
   | `fmt:check` / `lint` (frontend) | `make lint`, then fix what Oxlint/ESLint still report |
   | `typecheck` | vue-tsc error; after an API change check resource descriptors against the regenerated types |
   | `gen:api:check` | Generated client stale: `make gen-client` |
   | `check:architecture` | Import crosses UI layers ([frontend-concept.md](../../../docs/frontend-concept.md#tooling)) |
   | `check:unused` (knip) | Unused file/export/dependency: delete it or use it |
4. Frontend production build is not in `make check`: run `make check-frontend BUILD=1` (or `cd frontend && pnpm build`) for routing, config or dependency changes.
5. UI changed → also the visual review in the `design-system` skill. Passing checks do not replace it.
6. Report: commands run, mode (Postgres/SQLite), pass/fail, and anything skipped.
