# Backend concept

How to add and grow a domain. Folder roles: [architecture.md](architecture.md). Full working example: `backend/app/domains/organization/` (`user` and `auth` for extra cases).

A domain is `backend/app/domains/<name>/` with `models.py`, `schemas.py`, `filters.py`, `views.py`. Add `services/` when logic does not belong in the viewset. Add `tests/` next to the domain.

Viewsets stay thin: HTTP only — schema, permissions, queryset. **Almost no business logic in `views.py`.** Named workflows go into a **service class**.

---

## Model

Always inherit `BaseModel`. Declare each FK as the field plus a `_id: UUID` annotation. `related_name` is plural.

```python
from uuid import UUID
from tortoise import fields
from app.core.models import BaseModel

class Project(BaseModel):
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='projects', on_delete=fields.CASCADE
    )
    organization_id: UUID
    name = fields.CharField(max_length=255)

    class Meta:
        table = 'project'
        ordering = ['id']
```

See `app/domains/organization/models.py`.

---

## Schemas

- **Create** / **Update**: `BaseCreateSchema` + `@schema(model=...)`
- **Read**: `BaseReadSchema` + create fields; nest other read schemas for relations
- DTO not bound to one model: extend `BaseCreateSchema` or `BaseSchema`, **without** `@schema(model=...)`
- `organization` is set from auth in `process_state_to_model` — do not require it on create unless the endpoint is org-agnostic
- Group schemas with section comments (`# PROJECT_SCHEMAS`) when the file has more than one model

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

See `app/domains/organization/schemas.py`.

---

## Filters

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

---

## Views

One `APIRouter` + viewset per resource. Read-only → `BaseReadOnlyViewSet`. PATCH → set `update_schema`. Extra endpoints → `@action`.

```python
from fastapi import APIRouter
from fastapi_ronin.decorators import viewset
from app.core.viewsets import BaseModelViewSet
from app.domains.project.filters import ProjectFilterSet
from app.domains.project.models import Project
from app.domains.project.schemas import ProjectCreateSchema, ProjectReadSchema, ProjectUpdateSchema

projects_router = APIRouter(prefix='/projects', tags=['projects'])

@viewset(projects_router)
class ProjectViewSet(BaseModelViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema
    update_schema = ProjectUpdateSchema
    filterset_class = ProjectFilterSet
```

Custom create/destroy/queryset: `perform_create`, `perform_destroy`, `get_queryset` — see `OrganizationViewSet` / `OrganizationUserViewSet`. Superuser exceptions live on the viewset, not in `FilterObjectsManager`. If an action does more than wire CRUD, call a service — do not grow the viewset.

`BaseModelViewSet` requires `IsAuthenticated`. Lookup is UUID. Pagination: `page` / `page_size` (default `page_size=100`).

---

## Scoping

`get_queryset()` applies `FilterObjectsManager` automatically. Register every model in `app/shared/services/filter_objects_manager.py`:

```python
Project: Scope(
    user='org_users__user_id',
    organization='organization_id',
),
```

Empty `Scope()` means **no** auto-filter — override `get_queryset()` when the rule is custom (`OrganizationUserViewSet`).

---

## Services vs viewsets vs utils

| Put it here | When |
|---|---|
| Viewset | HTTP: which schema, who may CRUD, queryset shape. Keep this thin |
| `services/` class | Business workflow: validate, load related objects, persist, S3, websocket |
| `utils/` function | 5–20 lines, no identity as a “thing” (`round_number`, `date_utils`) |

Example: `OrganizationService` is a class in `domains/organization/services/organization_service.py`. If that class later needs several private helpers, turn it into `services/organization_service/organization_service.py` plus sibling modules — not a pile of functions in `utils/`.

### Service method shape

- **Main methods take model instances**, not ids (`invoice: Invoice`, not `invoice_id: UUID`). Resolve ids before the workflow runs.
- **More than three parameters** → a Pydantic schema **in the service file** (not `schemas.py` unless it is the HTTP DTO). Pass that schema in.
- **Heavy validation / loading** → a `validate_*` method: HTTP schema in → fetch objects, check rules → return a service schema of instances. The main method only receives that.

```python
class IssueInvoiceData(BaseModel):
    organization: Organization
    customer: Customer
    lines: list[InvoiceLine]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class InvoiceService:
    async def validate_issue(self, data: InvoiceCreateSchema) -> IssueInvoiceData:
        organization = await Organization.get(id=data.organization_id)
        customer = await Customer.get(id=data.customer_id)
        # rules that can fail go here
        return IssueInvoiceData(organization=organization, customer=customer, lines=...)

    async def issue(self, data: IssueInvoiceData) -> Invoice:
        ...
```

The viewset calls `validate_issue` then `issue`. It does not load models or encode business rules.

---

## Registration

1. `app/core/database.py` — `'app.domains.project.models'` in `MODELS`
2. `app/main.py` — `api_router.include_router(projects_router)`
3. `filter_objects_manager.py` — `Scope` for the model
4. Tell the user a migration is needed (`make mm` then `make m`). Do not run it unless they ask.

---

## Tests

Write backend tests when the behavior is not obvious CRUD: uniqueness, permissions, custom `get_queryset`, password/token flows, anything an agent or a later change can silently break. Skip a test only for a thin viewset that just wires schema + model.

```
app/domains/<name>/tests/test_<subject>.py
app/core/tests/test_<subject>.py          # health, auth, kernel
```

Shared Tortoise fixture: `app/conftest.py` (`db`) + `@pytest.mark.asyncio`. Prefer `TestClient` without DB when persistence is not required.

Canonical example: `app/domains/organization/tests/test_organization.py`. Also `app/core/tests/test_health.py`.

Run: `make t` (or `make test`). Do not add a frontend test suite unless the user asks.
