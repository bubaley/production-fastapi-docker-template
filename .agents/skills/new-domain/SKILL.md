---
name: new-domain
description: Add a new business entity end to end (backend domain + frontend feature) in this FastAPI + Nuxt template, then self-review it against the backend rules. Use when the user asks to add a domain, model, entity, CRUD screen, resource or "a list of X" to the product, or invokes new-domain (/new-domain, $new-domain). Not for extending an existing domain.
---

# New domain

Scaffold first, then shape. Rules live in the docs; this is the order of work.

1. **Name it.** Singular snake_case (`invoice`, `work_order`), Russian titles: plural for the list/drawer, singular for the card. Check [docs/product.md](../../../docs/product.md) — the entity must be a real scenario there or one the user just asked for.
2. **Scaffold:** `make new-domain name=<snake_name> title="Счета" item_title="Счёт"` (`plural=<snake_plural>` if the default is wrong). It refuses to overwrite; read its "Next steps".
3. **Backend fields** in `backend/app/domains/<name>/`: `models.py` (keep `organization` FK + `tenant_scope` unless the user says otherwise), `schemas.py` (separate update schema; immutable ownership fields only on create), `filters.py`. Non-CRUD logic → `services/<name>_service.py` class. Rules: [backend-concept.md](../../../docs/backend-concept.md) (Model, Schemas, Views, Scoping, Services).
4. **Tests:** extend `tests/test_<name>.py` for every non-obvious rule. Run `cd backend && uv run pytest app/domains/<name> --sqlite` (no migration exists yet).
5. **Migration:** do NOT run `make mm` / `make m`. Tell the user the domain needs a migration and ask them to run both (`ALLOW_MIGRATIONS=1` only after their explicit yes; in Claude Code a hook enforces this).
6. **Client:** `make gen-client`, then adapt `frontend/app/features/<camelName>/resources/<camelName>.ts` (form type, `toCreate`/`toUpdate`) and the list/detail views. UI copy Russian; App* components only — [frontend-concept.md](../../../docs/frontend-concept.md) (Resource descriptor, Templates).
7. **Navigation:** the scaffolder added an entry to `frontend/app/navigation/settings.ts` with a `Folder` icon — pick a fitting Lucide icon; set `superuserOnly` if needed. Main-app (non-settings) screens go to `layouts/default.vue` instead.
8. **Docs:** add the scenario to `docs/product.md` (what the user can see and do).
9. **Self-review the backend diff** (`git diff HEAD -- backend/`) against [backend-concept.md](../../../docs/backend-concept.md) and the canonical `backend/app/domains/organization/`; fix every miss:
   - every model has `tenant_scope` (`Scope(user=...)`, plus `organization=` for org data) or `Unscoped(reason=...)` with a real reason; no superuser bypass inside the scope;
   - models inherit `BaseModel`, FK + `<name>_id: UUID` annotation, plural `related_name`, `Meta.table` and `ordering`;
   - Create / Update / Read schemas; ownership fields never in Update; `organization` from auth, not the body;
   - viewset is thin (schema, permissions, queryset, filterset) and `views.py` exports `routers`; loading and rule checks live in the service (`validate_*`);
   - errors via `AppException.from_attrs(ErrorCode...)`; router has a plural kebab tag, actions have return types, `openapi.json` + generated client regenerated;
   - tests cover the non-obvious rules and tenant isolation, using the `auth_headers` / `*_factory` fixtures.
10. **Verify:** `make lint`, then `make check` (`PYTEST_ARGS=--sqlite` until the user has migrated). UI → the `design-system` skill's visual review.
11. **Commit:** `feat(<name>): …` — one feature per commit series. Report the pending migration to the user.
