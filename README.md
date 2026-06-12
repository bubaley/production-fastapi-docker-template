# Foliera

Full-stack starter for internal apps with multi-organization access: CRUD entities, authentication, drawer navigation, and ready-made UI primitives for lists and forms.

## Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Tortoise ORM, fastapi-ronin, Taskiq, Redis, PostgreSQL |
| Frontend | Nuxt 4, Vue 3, Pinia, PrimeVue, Tailwind CSS |
| Infra | Docker Compose, Caddy (prod), Makefile |

The backend exposes a REST API (`/api/v1`); the frontend is an SPA with a repo layer on top of `$api`. Data is scoped by user and current organization via `FilterObjectsManager`.

Detailed patterns for agents and developers live in `.cursor/rules/`.

---

## Quick start

### 1. Environment

```bash
cp .env.example .env
make install          # uv sync + pnpm install
docker compose up -d  # PostgreSQL + Redis
make m                # apply migrations
```

### 2. Run

In two terminals:

```bash
make rb   # backend → http://localhost:8000
make rf   # frontend → http://localhost:8080
```

For background tasks:

```bash
make rt   # Taskiq scheduler + worker
```

Other useful commands: `make mm` (create migrations), `make help`.

---

## Adding a new entity

Below is the minimal path from model to drawer item. See `.cursor/rules/backend-domain-pattern.mdc` and `.cursor/rules/frontend-feature-pattern.mdc` for details.

### Backend: domain

Create `backend/app/domains/<name>/` with four files.

**models.py**

```python
from tortoise import fields
from app.core.models import BaseModel

class Project(BaseModel):
    name = fields.CharField(max_length=255)

    class Meta:
        table = 'project'
        ordering = ['id']
```

**schemas.py**

```python
from fastapi_ronin.decorators import schema
from app.core.models import BaseCreateSchema, BaseReadSchema
from app.domains.project.models import Project

@schema(model=Project)
class ProjectCreateSchema(BaseCreateSchema):
    name: str

@schema(model=Project)
class ProjectUpdateSchema(BaseCreateSchema):
    name: str

@schema(model=Project)
class ProjectReadSchema(BaseReadSchema, ProjectCreateSchema):
    pass
```

**filters.py**

```python
from fastapi_ronin import filters
from app.domains.project.models import Project

class ProjectFilterSet(filters.FilterSet):
    fields = [
        filters.CharFilter('name', view_name='search', default_lookup='icontains'),
    ]

    class Meta:
        model = Project
```

**views.py**

```python
from fastapi import APIRouter
from fastapi_ronin.decorators import viewset
from app.core.viewsets import BaseModelViewSet
from app.domains.project.filters import ProjectFilterSet
from app.domains.project.models import Project
from app.domains.project.schemas import (
    ProjectCreateSchema,
    ProjectReadSchema,
    ProjectUpdateSchema,
)

projects_router = APIRouter(prefix='/projects', tags=['projects'])

@viewset(projects_router)
class ProjectViewSet(BaseModelViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema
    update_schema = ProjectUpdateSchema
    filterset_class = ProjectFilterSet
```

**Registration**

1. `backend/app/core/database.py` — add `'app.domains.project.models'` to `MODELS`
2. `backend/app/main.py` — `api_router.include_router(projects_router)`
3. `backend/app/shared/services/filter_objects_manager.py` — register model scoping
4. `make mm && make m`

### Frontend: feature

Create `frontend/app/features/project/`:

**models/project.ts** — type + `createCodec` (decode/encode)

**repos/projectRepo.ts** — `defineStore` + `getRepoConfig({ resource: 'projects', codec })`

**views/ProjectListView.vue** and **views/ProjectDetailView.vue** — built on `AppListTemplate` / `AppDetailTemplate`

**Registration**

1. `frontend/app/shared/composables/useRepo.ts` — `project: useProjectRepo`
2. Pages:
   - `frontend/app/pages/settings/projects/index.vue` → `<ProjectListView />`
   - `frontend/app/pages/settings/projects/[id].vue` → `<ProjectDetailView />`
3. Drawer — `frontend/app/layouts/settings.vue`:

```typescript
{ to: { name: 'settings-projects' }, label: 'Projects', icon: 'lucide:folder' }
```

Nuxt route names are derived from the file path: `settings/projects/[id].vue` → `settings-projects-id`.

---

## UI components (read before frontend work)

Review the primitives in `frontend/app/shared/ui/` first:

| Component | Role |
|---|---|
| `AppSection` | Page/section wrapper: `title`, `description`, `backAction` |
| `AppList` | Table or list with search (`showSearch`) and pagination |
| `AppListTemplate` | `AppSection` + `AppList` + create button + detail modal |
| `AppDetailTemplate` | `AppSection` + form with save/delete via `AppDetailActions` |
| `AppModal` | Dialog with optional `title` / `subtitle` |
| `AppColumn` | DataTable column with `format` callback |
| `AppSelect` | Select backed by a repo (`:repo="useRepo('user')"`) |
| `AppTemplateActions` | Row of action buttons with per-action loading and optional toasts |

`AppTemplateActions` is a low-level block for custom action bars. It accepts `actions: AppTemplateAction[]` (label, icon, `action`, `successNotification`, `errorNotification`, `hidden`, `mode`). Used inside `AppDetailActions`; can be placed in `#actions` slots on `AppSection` / templates when you need custom buttons beyond standard save/delete.

`AppSection` uses `description` for the subtitle text (not `subtitle`). Layout variants: `templateVariant` — `page`, `section`, `flat-section`.

Live examples: `features/organization/views/`, `features/user/views/`.

---

## Repository structure

```
backend/app/
  core/           # settings, viewsets, auth, database
  domains/        # business modules (models, schemas, filters, views)
  shared/         # shared services (FilterObjectsManager, …)

frontend/app/
  features/       # domain modules (models, repos, views, components)
  pages/          # Nuxt routes (thin wrappers over views)
  shared/         # UI, composables, toolkits/repo
  layouts/        # default, settings, setup — drawer navigation
```

---

## Makefile cheat sheet

| Command | Action |
|---|---|
| `make install` | Install backend + frontend dependencies |
| `make mm` | Create migrations (tortoise makemigrations) |
| `make m` | Apply migrations |
| `make rb` | Run backend (uvicorn, reload) |
| `make rf` | Run frontend (nuxt dev) |
| `make rt` | Run Taskiq scheduler + worker |
| `make lint` | Ruff + ESLint |
| `make test` / `make t` | Run backend tests (pytest) |

---

## Testing (backend)

Tests live next to the code they cover:

```
backend/app/domains/<name>/tests/test_<subject>.py   # domain tests
backend/app/core/tests/test_<subject>.py             # app-level tests (health, auth, …)
```

Run them with:

```bash
make test          # or: make t
# equivalent:
cd backend && uv run manage.py test
# single domain:
cd backend && uv run manage.py test app/domains/organization/tests
# single file:
cd backend && uv run manage.py test app/core/tests/test_health.py
```

### Examples

**API smoke test** — no database required (`app/core/tests/`):

```python
# app/core/tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_returns_ok():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
```

**Tortoise model test** — in-memory SQLite via shared `db` fixture (`app/conftest.py`):

```python
# app/domains/organization/tests/test_organization.py
import pytest
from app.domains.organization.models import Organization

@pytest.mark.asyncio
async def test_create_organization(db):
    org = await Organization.create(name='Acme', key='acme')

    assert org.id is not None
    assert org.name == 'Acme'
    assert org.key == 'acme'
```

The `db` fixture is defined once in `app/conftest.py` using `tortoise_test_context` — each test gets an isolated in-memory database with schemas generated automatically.

### Conventions

- One `tests/` folder per domain; file name: `test_<subject>.py`
- Shared Tortoise fixture: `app/conftest.py` (`db`)
- Mark async tests with `@pytest.mark.asyncio`
- Prefer unit tests without DB when persistence is not required
- Use `TestClient` for endpoint smoke tests that do not need persistence