# Product

Product-owned spec: what this product does beyond the template. Inherited capabilities (sign-in, organizations, users and API tokens, tenant scoping, realtime, background tasks, files, theming, `/ui`, deployment) are in [template-core.md](template-core.md). When the two disagree, **this file wins**.

In the template repository this file describes the template's own demo product. `make init` replaces it with an empty skeleton with the same headings (`scripts/bootstrap/product.md.tmpl`); a product fills them in.

Agents: do not invent capabilities that are in neither file. Update this file in the same change as the behavior. UI copy is Russian.

---

## Purpose

A starter for internal multi-organization apps. The demo shows how a product screen is composed from the template's primitives so a new product can replace it with real domains (`make new-domain`).

## Personas

- **Product builder** (a developer or an AI agent) who starts a product from the template and needs working examples to copy.
- **Signed-in member** of an organization who uses the demo screens below.

## Scenarios

- **Публичная страница** (`/`) — заготовка: название продукта, короткий текст-заглушка и кнопка «Войти» («Перейти в приложение» для вошедшего). Продукт заменяет текст своим описанием.
- **Главная** (`/home`) — смена организации, переход в настройки и каталог UI, интерактивный пример AppPageView: действия в шапке, контекст под шапкой, поиск и переключатель под разделителем, прокручиваемые карточки и закреплённая нижняя зона. Поиск фильтрует возможности страницы; сброс возвращает исходный пример.

## Non-goals

- No business domain of its own: organizations, users and tokens are template core, not demo content.
- No public sign-up, billing, organization roles or email delivery.

## Changes to template behavior

None — the template itself.
