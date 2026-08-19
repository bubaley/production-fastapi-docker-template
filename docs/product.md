# Product

Starter template for internal multi-organization apps. Use it to bootstrap a project, then **rewrite this file** for the real product.

How-to and folder roles: [architecture.md](architecture.md), [backend-concept.md](backend-concept.md), [frontend-concept.md](frontend-concept.md).

---

## Purpose

A signed-in user works inside **one organization at a time**: settings, members, and later domain CRUD. There is no public signup — the first user is `python -m manage create_superuser`. After login, pick or create an organization; everything else is scoped to it.

User-facing copy is **Russian**. Code comments stay English.

Do not invent capabilities that are not listed here. When a scenario changes, update this file in the same change.

---

## Scenarios

### Access

- **Вход** (`/auth`) — email + password. Session via JWT cookies (`access_token` / `refresh_token`).
- **Выбор организации** (`/home/setup`) — required before the rest of the app. Creating an org adds the current user as a member.
- **Главная** — смена организации, настройки, каталог UI (`/home/ui`).

### Settings

- **Организации** — list / create / edit (`name` + unique `key`), members. `key` is the tenancy id (header `Organization-Key`).
- **Пользователи** (superuser only) — directory and passwords. Users are created here, then attached to an org as members. **Токены** — named API tokens; the secret is shown once (`Authorization: Token …`).
- **Профиль** — current user, change password, own tokens.

There are no org roles (admin / member / viewer) — only membership (`OrganizationUser`) and a global `is_superuser` flag.

---

## Important aspects

**`FilterObjectsManager`** — default queryset limit by current user / organization (`AuthState`). After adding a model, register it in `filter_objects_manager.py`. Empty `Scope()` means no auto-filter — then override `get_queryset()`. Superuser bypass is **per viewset**, not global.

**`OrganizationWebSocketService`** — `/ws` for organization realtime. Extend this service (events, `check_access`, `process_message`). Do not add a second websocket stack.

**Current org** — `useSetupStore` + `Organization-Key`. Backend resolves the header via `OwnedDataProvider` (user must belong to that org). Do not trust the client to POST an arbitrary organization on create; `process_state_to_model` sets it from auth.
