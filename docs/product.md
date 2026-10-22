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
- **Главная** — смена организации, настройки, каталог UI (`/ui`) и интерактивный пример AppPageView: действия в шапке, контекст под шапкой, поиск и переключатель под разделителем, прокручиваемые карточки и закреплённая нижняя зона. Поиск фильтрует возможности страницы; сброс возвращает исходный пример.
- **Оформление** — в меню профиля (иконка пользователя в шапке): тема «Системная / Светлая / Тёмная» и акцентный цвет (нейтральный, синий, фиолетовый, зелёный, оранжевый). Выбор сохраняется в cookie и применяется до первой отрисовки.

### UI catalogue

- **Каталог UI** (`/ui`) is public and uses local sample data. Its copy is English (including its theme and palette switch) so it reads alongside the prop names it demonstrates.
- Demonstrates the design tokens (colors, radii, control sizes, type scale), variant/size/tone matrices for App controls with disabled, loading and invalid states, forms, dates, selects, checkboxes, radio groups, switches, badges, tooltips, alerts, progress, skeletons, scroll areas, modals, drawers, menus, the image lightbox, page/section patterns, cards in semantic tones, AppTitle sizes, the Lucide icon picker and the color picker. Theme (system/light/dark) and palette switch at the top; tables switch between default and outline styles.
- `AppFilters` lets users add filter conditions through **+**. It is a reusable UI component; each feature still defines its supported fields and maps filter values to repo query parameters; the component adds no business filtering rules by itself.

### Settings

- **Организации** — list / create / edit (`name` + unique `key`), members. `key` is the tenancy id (header `Organization-Key`). В списке доступны поиск по названию, постоянный фильтр по точному ключу и добавляемое условие «ключ содержит»; условия применяются совместно и остаются на экране при прокрутке.
- **Пользователи** (superuser only) — directory and passwords. Users are created here, then attached to an org as members. **Токены** — named API tokens; the secret is shown once (`Authorization: Token …`).
- **Профиль** — current user, change password, own tokens.

Создание и удаление пользователей доступны только суперпользователю. Профиль
пользователя доступен и до выбора организации. При переименовании API-токена
его владелец неизменен; обычный пользователь управляет только своими токенами.

Выход очищает обе cookies сессии и выбранную организацию вместе с данными
репозиториев. Вход другим аккаунтом начинает выбор организации заново. Ошибка
загрузки карточки показывается на странице с действием «Повторить»; запоздалый
ответ предыдущей карточки не заменяет открытую карточку.

There are no org roles (admin / member / viewer) — only membership (`OrganizationUser`) and a global `is_superuser` flag.

---

## Important aspects

**Tenant scoping** — every model declares `tenant_scope` (`Scope(...)` or `Unscoped(reason=...)`); `FilterObjectsManager` applies it to every queryset and fails closed on models without one. Org-scoped models require the `Organization-Key` header. Superuser bypass is **per viewset**, not global. Memberships cannot be edited after creation — only added or removed.

**`OrganizationWebSocketService`** — `/ws` for organization realtime. Extend this service (events, `check_access`, `process_message`). Do not add a second websocket stack.

Подключение к `/ws/organizations/{organization_id}` требует действующего access
JWT (cookie или Bearer) либо API-токена и участия пользователя в организации.
Refresh JWT не авторизует API и WebSocket. Анонимные подключения и подключения
к чужим организациям отклоняются; новых событий шаблон по-прежнему не отправляет.

**Current org** — `useSetupStore` + `Organization-Key`. Backend resolves the header via `OwnedDataProvider` (user must belong to that org). Do not trust the client to POST an arbitrary organization on create; `process_state_to_model` sets it from auth.

### List scrolling

- Списки на AppListTemplate автоматически подгружают следующую страницу при прокрутке до конца. Уже показанные строки сохраняются; при ошибке доступен повтор запроса. Поиск и смена фильтров начинают выдачу с первой страницы.
- Постраничный режим остаётся доступен через `infiniteScroll=false`; локальные списки без репозитория не запускают автоматические запросы.
- Поиск и фильтры списков остаются на экране при прокрутке.
