# Template core

Capabilities every product built from this template inherits. **Template-owned**: forks receive changes to this file through the `sync-template` skill ([template-ownership.md](template-ownership.md)) and do not edit it — product-specific changes go to [product.md](product.md), which wins when the two disagree.

Behavior only; how it is built: [architecture.md](architecture.md), [backend-concept.md](backend-concept.md), [frontend-concept.md](frontend-concept.md), [deployment.md](deployment.md). UI copy is **Russian**; code comments English.

---

## Access and session

- **No public sign-up.** The first user is created from the command line (`make createsuperuser`); a superuser creates everyone else.
- **Публичная страница** (`/`) renders on the server with title, description and `og:*` meta. It shows «Войти», or «Перейти в приложение» for a signed-in visitor. Its text belongs to the product ([product.md](product.md)).
- **Вход** (`/auth`) — email + password. The API sets HttpOnly cookies (`access_token`, `refresh_token`); the browser never sees a token. An expired access cookie is renewed silently; a dead session returns to `/auth` and back to the requested page after sign-in.
- Repeated failed logins from one client and email are rate-limited (429). Unknown email, wrong password and an inactive user get the same answer.
- **Выход** clears both cookies, the chosen organization and all loaded data; signing in as someone else starts over. «Выйти на всех устройствах» ends every session of the user. Changing a password, deactivating a user or `logout-all` invalidates all of that user's tokens.

## Organizations and membership

- A signed-in user works inside **one organization at a time**. **Выбор организации** (`/home/setup`) comes before the rest of the app (the profile is reachable without it). The choice is remembered per user.
- Creating an organization makes the creator a member. `name` is editable; `key` is the tenancy id (header `Organization-Key`) and fixed after creation.
- **Настройки → Организации**: list with search by name, a fixed exact-key filter and an addable "key contains" condition; detail with members. Members are added to the organization being viewed (not the active one) and can only be added or removed.
- There are **no organization roles** — only membership and the global `is_superuser` flag.

## Users and API tokens

- **Настройки → Пользователи** (superuser only): directory, create and delete users, set passwords. A user is attached to an organization as a member afterwards.
- **Профиль** (`/settings/profile`): own data, password change, own API tokens, «Выйти на всех устройствах».
- **Токены**: named API tokens (`Authorization: Token …`) with optional expiry; the secret is shown once. Renaming keeps the owner; a regular user manages only their own tokens; a request authenticated by an API token cannot create tokens.

## Tenant scoping

- Every model declares its scope; a model without one fails closed (no data, test failure). Organization-scoped data requires `Organization-Key` and is visible only to members of that organization; a forged or foreign key resolves nothing.
- Superusers see beyond their memberships only where a viewset explicitly allows it (users, memberships, API tokens).

## Realtime, background tasks, files

- **Realtime**: `/ws/organizations/{organization_id}` for members of that organization (access cookie, access JWT or API token; refresh tokens do not work). Connections are re-checked while open and closed when access ends. The template sends no events yet.
- **Background tasks**: Taskiq on Redis streams, acknowledged after execution (a crashed worker does not lose them); results expire. Tasks live next to their domain. Example: `notify_organization_members`.
- **Files**: S3-compatible storage with private objects; access through presigned download/upload URLs. Nothing in the UI uses it yet.

## UI

- **Оформление** (profile menu): theme «Системная / Светлая / Тёмная» and accent palette (нейтральный, синий, фиолетовый, зелёный, оранжевый), stored in a cookie and applied before first paint.
- **Lists** load the next page on scroll, keep shown rows, offer retry on error, keep search and filters on screen, and restart from page 1 when they change. **Detail cards** show a loading state, an error with «Повторить», and never replace an open card with a late response for another one.
- **Каталог UI** (`/ui`, public): every App* primitive with variants, states, tones, themes and palettes on local sample data. Its copy is English on purpose (it sits next to prop names).

## Operations

- One Docker image (Caddy, API, Nuxt, Taskiq worker/scheduler) that applies migrations on start, exposes `/health` and `/ready`, and exits when a service dies.
- CI on every pull request; on `main` conventional commits decide the next version, the changelog and the release; the image is published and deployed by digest ([deployment.md](deployment.md)).

## Agent tooling

- `make init name=…` turns a template copy into a product; `make new-domain name=…` scaffolds a CRUD entity end to end; the `sync-template` skill pulls template changes into a fork.
- Agent skills shared by Claude Code and Codex live in `.agents/skills/`; Claude Code project hooks block migration commands and format edited files ([architecture.md](architecture.md#agent-tooling)).
