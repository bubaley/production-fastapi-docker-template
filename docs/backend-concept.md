# Backend concept

How to add and grow a domain. Folder roles: [architecture.md](architecture.md). Full working example: `backend/app/domains/organization/` (`user` and `auth` for extra cases).

A domain is `backend/app/domains/<name>/` with `models.py`, `schemas.py`, `filters.py`, `views.py`. Add `services/` when logic does not belong in the viewset. Add `tests/` next to the domain.

Viewsets stay thin: HTTP only — schema, permissions, queryset. **Almost no business logic in `views.py`.** Named workflows go into a **service class**.

---

## Model

Always inherit `BaseModel`. Declare each FK as the field plus a `_id: UUID` annotation. `related_name` is plural. Every model declares `tenant_scope` (see [Scoping](#scoping)).

```python
from uuid import UUID
from tortoise import fields
from app.core.models import BaseModel
from app.core.scope import Scope

class Project(BaseModel):
    organization = fields.ForeignKeyField(
        'models.Organization', related_name='projects', on_delete=fields.CASCADE
    )
    organization_id: UUID
    name = fields.CharField(max_length=255)

    tenant_scope = Scope(
        user='organization__org_users__user_id',
        organization='organization_id',
    )

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

Always declare a separate update schema for resources with immutable ownership.
Ronin falls back to the create schema when `update_schema` is missing. For example,
`UserTokenUpdateSchema` accepts only `name` and rejects extra fields; `user_id`
belongs only to creation. Do not let a PATCH/PUT payload change a token's owner.
`OrganizationUserUpdateSchema` has no fields and forbids extras: a membership's
user and organization are fixed once created.

```python
from fastapi import APIRouter
from fastapi_ronin.decorators import viewset
from app.core.viewsets import BaseModelViewSet
from app.domains.project.filters import ProjectFilterSet
from app.domains.project.models import Project
from app.domains.project.schemas import ProjectCreateSchema, ProjectReadSchema, ProjectUpdateSchema

projects_router = APIRouter(prefix='/projects', tags=['projects'])
routers = (projects_router,)  # picked up by app/core/discovery.py

@viewset(projects_router)
class ProjectViewSet(BaseModelViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema
    update_schema = ProjectUpdateSchema
    filterset_class = ProjectFilterSet
```

Routes and their operationIds (see [OpenAPI contract](#openapi-contract)): `list` (GET), `create` (POST), `retrieve` (GET), `update` (PUT), `partial_update` (PATCH), `destroy` (DELETE), plus one per `@action` named after the method. PUT and PATCH both run with `self.action == 'update'`.

The viewset declares the optional `Organization-Key` header in OpenAPI on all its routes when the model is organization-scoped (`Scope(organization=...)`) or has an `organization` FK filled from the header on create. Set `organization_header = False` when the organization comes from the body instead (`OrganizationUserViewSet`), `True` to force it.

Custom create/destroy/queryset: `perform_create`, `perform_destroy`, `get_queryset` — see `OrganizationViewSet` / `OrganizationUserViewSet`. Superuser exceptions live on the viewset, not in `FilterObjectsManager`. If an action does more than wire CRUD, call a service — do not grow the viewset.

`BaseModelViewSet` requires `IsAuthenticated`. Lookup is UUID. Pagination: `page` / `page_size` (default `page_size=100`). Pagination appends `id` to the ordering (`with_stable_ordering`), so a non-unique `Meta.ordering` such as `created_at` still yields stable pages; keep `Meta.ordering` for the business order only.

---

## Scoping

`get_queryset()` passes every queryset through `FilterObjectsManager`, which reads the model's `tenant_scope` (`app/core/scope.py`). It **fails closed**:

| Declaration | Effect |
|---|---|
| none | `ScopeConfigurationError` on the first query. `app/shared/tests/test_filter_objects_manager.py` fails for every registered model without a scope |
| `Scope(user=...)` | Rows matching the current user only. The user rule is mandatory; anonymous state is rejected (401) |
| `Scope(user=..., organization=...)` | User rule **and** the organization from `Organization-Key`. No header → 400 `Organization-Key header is required` |
| `Scope(..., require_organization=False)` | Without the header only the user rule applies: rows from every organization the user belongs to, never other tenants |
| `Unscoped(reason='...')` | No filter. Only for intentionally global reference data |

Each rule is a lookup path compared with `=` (`'organization__org_users__user_id'`) or a callable `value -> Q` for custom rules, e.g. a subquery (`OrganizationUser` uses one because Tortoise mis-aliases a self-join).

```python
tenant_scope = Scope(
    user='organization__org_users__user_id',  # Project -> Organization -> OrganizationUser
    organization='organization_id',
)
```

The user rule always applies, so a forged or stale `Organization-Key` cannot widen access. Superuser bypass lives on the viewset (`if user.is_superuser: return Model.all()`, else `await super().get_queryset()`), not in the scope.

`organization` is assigned from `AuthState` on **create only** (`process_state_to_model` in `BaseGenericViewSet.before_save`); an update never moves a row to another organization.

---

## Services vs viewsets vs utils

| Put it here | When |
|---|---|
| Viewset | HTTP: which schema, who may CRUD, queryset shape. Keep this thin |
| `services/` class | Business workflow: validate, load related objects, persist, S3, websocket |
| `utils/` function | 5–20 lines, no identity as a “thing” (`date_utils`, `get_details_from_exception`) |

Example: `OrganizationService` is a class in `domains/organization/services/organization_service.py`. If that class later needs several private helpers, turn it into `services/organization_service/organization_service.py` plus sibling modules — not a pile of functions in `utils/`.

`OrganizationService.create` saves the organization and the actor's membership in
one transaction. A membership is created for the organization named in the body
(`POST /organization-users` with `organization_id` + `user_id`), never the
`Organization-Key` one: members are managed from the organization's own page. Membership addition, update and removal validate access through
`validate_membership_change`; duplicate membership uses the database uniqueness constraint.
The viewsets only delegate these workflows to the service.

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

## Errors

Every error response uses one envelope (`ResultData`, `app/core/exceptions.py`):

```json
{"data": null, "error": {"code": "NOT_FOUND", "message": "Not found", "details": {}}, "success": false}
```

Raise `AppException.from_attrs(ErrorCode.FORBIDDEN, 'Cannot modify this organization')` for business errors; its status follows the code (`UNAUTHORIZED` 401, `FORBIDDEN` 403, `NOT_FOUND` 404, `CONFLICT` 409, `RATE_LIMITED` 429, otherwise 400). `headers=` adds response headers (e.g. `Retry-After`). A plain `HTTPException` also works: the status picks the code (400/422 `VALIDATION_ERROR`, 401, 403, 404, 409, other 4xx `APP_ERROR`, 5xx `UNHANDLED_ERROR`). Request/pydantic validation → 422 with `details.errors`. Tortoise `DoesNotExist` → 404, `IntegrityError` → 409 without the database message. Unexpected exceptions → 500 `Internal server error`; the exception is logged, never returned.

---

## Registration

Domains are discovered, not registered (`app/core/discovery.py`):

1. Every package `app/domains/<name>/` (with `__init__.py`) is a domain. Its `models.py` joins Tortoise `MODELS`; its `views.py` must export `routers = (projects_router, …)` (or a single `router`), which are mounted under `/api/v1`. A domain without HTTP has no `views.py`.
2. Order is deterministic: kernel domains `auth`, `user`, `organization` first, then the rest alphabetically; inside a domain, the order of `routers`. It decides the path order in `openapi.json`.
3. A domain module that fails to import (or exports no router) stops the app with `DomainDiscoveryError` naming the module — fix it, do not catch it.
4. `tenant_scope` on every model (`Scope(...)` or `Unscoped(reason=...)`).
5. Tell the user a migration is needed (`make mm` then `make m`). Do not run it unless they ask.

---

## Auth and tokens

FastAPI owns auth. Lifecycle lives in `AuthService` (`domains/auth/services/auth_service.py`); JWT encoding in `TokenService`; how tokens travel in `domains/auth/transport.py`; credential resolution and CSRF in `core/auth.py` + `core/csrf.py`. Viewsets only call the service and set/clear cookies. **Tokens never appear in a response body.**

### Endpoints (`/api/v1/auth`)

| Endpoint | Auth | Request | Response |
|---|---|---|---|
| `POST /login` | public | `{email, password}` | 200 `SessionSchema` `{user, organizations, access_expires_at, refresh_expires_at}`; sets both cookies |
| `POST /refresh` | public; reads only the `refresh_token` cookie | no body | 200 `SessionExpirySchema` `{access_expires_at, refresh_expires_at}`; rotates both cookies. 401 without/with an invalid cookie |
| `POST /logout` | public (works with expired credentials) | no body | 204; revokes the session family, clears cookies |
| `POST /logout-all` | authenticated | no body | 204; invalidates every JWT of the user, clears cookies |
| `GET /me` | authenticated | — | 200 `MeSchema` `{user, organizations}` — `user.is_superuser`; `organizations` are the user's memberships (also for superusers) |

`POST /users/{id}/change-password` returns fresh cookies when users change their own password.

### Cookies

| Cookie | Path | Lifetime | Attributes |
|---|---|---|---|
| `access_token` | `/` | `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (15) | HttpOnly, `SameSite=COOKIE_SAMESITE` (lax), `Secure=COOKIE_SECURE` |
| `refresh_token` | `REFRESH_COOKIE_PATH` (`/api/v1/auth`) | `JWT_REFRESH_TOKEN_EXPIRE_MINUTES` (30 days) | same |

A client keeps no token: on 401 it calls `POST /auth/refresh` once and retries; a 401 from refresh means signed out.

### Request authentication

Credentials resolve in order, first valid wins: `access_token` cookie → `Authorization: Token <api token>` → `Authorization: Bearer <access JWT>`. An expired cookie does not hide a valid header. Bearer stays for tests (`auth_headers`) and server-side scripts that mint tokens with `AuthService.start_session`; the API never hands a JWT to clients. Websockets use the same resolution — browsers authenticate with the access cookie (same origin, no token in the URL).

### CSRF

An unsafe request (`POST`/`PUT`/`PATCH`/`DELETE`) that relies on the auth cookies — authenticated by the access cookie, or a public auth route carrying an auth cookie — must send `Origin` (fallback: `Referer`) equal to the request host or listed in `CORS_ORIGINS`; otherwise 403 `FORBIDDEN` `Origin not allowed`. `Origin: null` is rejected. Safe methods are never checked; requests authenticated by an `Authorization` header are exempt (a cross-site page cannot set it). `SameSite=Lax` is the first layer; the Origin check also covers same-site attackers.

### SSR contract

During SSR, Nitro calls FastAPI server-to-server (internal URL `http://127.0.0.1:8000` in the image) and forwards the incoming request's `Cookie` header. That works for **GET** without `Origin`. Nitro should not issue unsafe requests during SSR; if it must, it forwards the browser's `Origin` too (the public origin must then be in `CORS_ORIGINS`, since the Host is the internal one). An expired access cookie during SSR yields 401: render anonymous or client-only and let the browser refresh; if Nitro refreshes itself, it must relay `Set-Cookie` to the browser.

### Lifecycle rules

| Rule | Detail |
|---|---|
| Claims | `sub`, `type` (`access`/`refresh`), `iat`, `exp`, `jti`, `ver` (= `User.token_version`), `sid` (session family) |
| Legacy tokens | `id` instead of `sub`, no `jti`/`ver`: accepted while `JWT_ACCEPT_LEGACY_TOKENS=true`; a legacy refresh token is exchanged once. Turn the flag off (and later delete the branch in `TokenService.decode`) once tokens issued before this change have expired (refresh lifetime, 30 days by default) |
| Refresh rotation | Every refresh revokes the presented token (`RefreshSession`) and issues a new pair in the same family. Reusing a rotated token revokes the whole family; within `REFRESH_REUSE_LEEWAY_SECONDS` (parallel tabs) it only gets 401 |
| Global invalidation | `AuthService.invalidate_user_tokens(user)` bumps `token_version` and revokes all refresh sessions. Called by password change, `POST /auth/logout-all`, deactivation (`is_active=False`) |
| Inactive users | `is_active=False` cannot log in, refresh or use any token, API tokens included |
| API tokens | `Authorization: Token …`; optional `expires_at`; `last_used_at` written at most every `API_TOKEN_TOUCH_INTERVAL_SECONDS`; a request authenticated by an API token cannot create API tokens (`AuthState.auth_method`) |
| Login protection | Failed logins counted per client IP + email (`login_rate_limiter`, Redis, memory fallback); over `LOGIN_RATE_LIMIT_ATTEMPTS` → 429 with `Retry-After`. Unknown email, wrong password and inactive user return the same 401 |
| Input | `NewPassword` (min `PASSWORD_MIN_LENGTH`) for every password a user sets; `NormalizedEmail` (validated, lowercased) for emails that are stored; `LoginEmail` (lowercased only) for login |

Superuser-only user fields (`is_superuser`, `is_active`) are guarded in `UserService.validate_update`.

---

## OpenAPI contract

The schema is the frontend's API contract: `make openapi` (`manage.py openapi --output ../frontend/openapi.json`, no database or Redis) writes `frontend/openapi.json`, which is committed and feeds the generated client. `app/core/tests/test_openapi.py` fails when the committed file is stale, when operationIds collide or break the convention, and when FastAPI warns while building the schema. Conventions live in `app/core/openapi.py`:

| Convention | How |
|---|---|
| operationId | `<first tag>_<route name>`, snake_case: `organizations_list`, `organizations_partial_update`, `organization_users_create`, `auth_login`, `users_change_password`. Generated client functions take these names, so renaming a route or tag is a breaking change |
| Tags | One per router, plural kebab-case resource (`organization-users`) |
| Errors | `api_router` has `responses=ERROR_RESPONSES`: every operation documents `ErrorResponse` (`{data: null, error: {code, message, details}, success: false}`) for 400/401/403/404/409/422/429/500 |
| Security | `cookieAuth` (apiKey cookie `access_token`), `tokenAuth` (apiKey header `Authorization`, `Token …`), `bearerAuth` (HTTP bearer JWT). Public auth routes (`PUBLIC_PATHS` in `core/auth.py`) declare `security: []` |
| Response models | Every endpoint has one: a return annotation on `@action` (or `response_model=`), `status_code=204` with `-> None` for empty responses, `status_code=201` for creation |
| List responses | `PageResponse` → `<ReadSchema>Page` (`{data, meta: {page, page_size, has_next}}`) |

When adding an endpoint: give the router a tag, the action a meaningful method name and a return type (a schema, not `dict`), raise `AppException` for errors (the envelope is already documented), then run `make openapi` and commit the JSON with the change.

---

## Health, logging, telemetry

- `GET /health` — liveness, no dependencies, returns `version` (`APP_VERSION`) and `sha` (`GIT_SHA`). `GET /ready` — `SELECT 1` and Redis ping with a 2 s timeout, 503 when either fails. Both are hidden from OpenAPI and excluded from tracing.
- Redis is not a boot requirement: lifespan logs a warning if the broker cannot start; `/ready` reports it.
- Logging is loguru only (`app/core/logging.py`, `setup_logging()` in the API and the taskiq worker). `LOG_FORMAT=json` in production, `text` locally; stdlib loggers (uvicorn access/error, taskiq, tortoise) are routed through it. Log with `from loguru import logger`; never `print`.
- Every line carries `request_id` (`RequestIdMiddleware`): a sane incoming `X-Request-ID` is reused, otherwise generated, and returned on every response. Unhandled errors are logged once, with the request id.
- OpenTelemetry: FastAPI's native telemetry. `uv sync --extra otel`, `OTEL_ENABLED=true` and the standard `OTEL_EXPORTER_OTLP_ENDPOINT` / `OTEL_SERVICE_NAME`.

---

## WebSockets

Subclass `BaseWebSocketService` (canonical: `OrganizationWebSocketService`), override `check_access` (use `await self.get_authentication(websocket)`), call `register_routes(ws_router)` in `main.py`.

- `send_message(...)` publishes through Redis pub/sub; every API process delivers to its own connections. Call it from anywhere, including taskiq tasks. Without Redis it falls back to local delivery.
- Payloads go through `jsonable_encoder` (UUID, datetime, pydantic models are fine).
- Each send has `WEBSOCKET_SEND_TIMEOUT_SECONDS`; a slow or dead client is closed (1013) and dropped.
- Handshake: Origin must be same-origin or in `CORS_ORIGINS` (clients without Origin are allowed), then `check_access`. Rejected handshakes close with 1008.
- Connected clients are re-checked every `WEBSOCKET_AUTH_CHECK_INTERVAL_SECONDS` and when the access token expires: 4401 when the credential is gone (expired, revoked, user inactive), 4403 when access is gone. Messages over `WEBSOCKET_MAX_MESSAGE_BYTES` close with 1009.

---

## Background tasks (taskiq)

The broker is `RedisStreamBroker` (acknowledged after execution) with a result backend whose results expire after `TASKIQ_RESULT_TTL_SECONDS`. Tests use `InMemoryBroker` (selected by `TESTING`).

1. Put tasks in `app/domains/<name>/tasks.py` — the worker discovers `app/**/tasks.py`.
2. `@broker.task(task_name='<domain>.<action>')`; arguments must be JSON-serializable (ids, not model instances); load models inside the task.
3. Enqueue with `await my_task.kiq(...)`; the worker has Tortoise and logging initialised.
4. Test with `await (await my_task.kiq(...)).wait_result()`.

Example: `app/domains/organization/tasks.py` (`notify_organization_members`) and its test.

---

## File storage (S3)

`get_s3_service()` returns a lazy `S3Service` (no AWS call until first use; blocking calls run in a thread).

- `upload(file, filename, prefix=None)` streams a file-like object (`UploadFile.file`) under `<prefix>/YYYY/MM/DD/<uuid><.ext>`; the client filename only contributes a sanitized extension. Store the returned `key`, not the URL.
- Objects are private (no ACL). Give access with `presigned_get_url(key, download_name=...)`; let browsers upload directly with `presigned_put_url(key, content_type)`. `public_url(key)` is for a public bucket/CDN (`AWS_S3_PUBLIC_URL`).
- `delete(key)`. Failures raise `S3Error` with the boto error as `__cause__`.

---

## Tests

Write backend tests when the behavior is not obvious CRUD: uniqueness, permissions, custom `get_queryset`, password/token flows, anything an agent or a later change can silently break. Skip a test only for a thin viewset that just wires schema + model.

```
app/domains/<name>/tests/test_<subject>.py
app/core/tests/test_<subject>.py          # health, auth, kernel
app/shared/tests/test_<subject>.py        # cross-domain services (scoping, async_task)
```

`app/conftest.py` sets `TESTING=true` before importing the app: in-memory taskiq broker, pub/sub and rate limiter, bcrypt cost 4. Fixtures:

| Fixture | Use |
|---|---|
| `db` | Tortoise context |
| `api_client` | The real ASGI app over `httpx2` (no lifespan: no Redis, no broker startup). Keeps cookies and sends `Origin: http://test` like a same-origin browser, so cookie sessions pass the CSRF check |
| `user_factory(is_superuser=, is_active=, email=)` | Users with password `TEST_PASSWORD` (`test-password`) |
| `organization_factory(members=(user,), name=)`, `membership_factory(user, org)` | Tenants |
| `auth_headers(user, org=None)` | `await auth_headers(user, org)` → Bearer token of a fresh session plus `Organization-Key`. With cookies in the client jar the cookie wins (resolution order); pass `'Cookie': ''` to test a header credential alone |
| `websocket_fanout` | Subscribes registered websocket services to the in-memory pub/sub |

Get tokens through `auth_headers` or `AuthService.start_session(user)`, never by hand-encoding JWTs. `asyncio_mode = "auto"`; `@pytest.mark.asyncio` is still written for clarity. Prefer `TestClient` without `db` when persistence is not required (`app/core/tests/test_exceptions.py`).

Two database modes, chosen per run:

| Mode | Command | What happens |
|---|---|---|
| PostgreSQL (default, CI) | `make t` → `uv run manage.py test --keepdb` | Separate `<SQL_DATABASE>_test` database; migrations are applied once per session, tables truncated per test. Without `--keepdb` an existing test database is dropped (asks first in a terminal) |
| SQLite | `cd backend && uv run pytest --sqlite` | Fresh in-memory schema per `db` fixture, no migrations, no PostgreSQL needed |

SQLite covers API behavior and permissions, not PostgreSQL migrations or engine-specific SQL. Production databases are never touched in either mode.

Canonical example: `app/domains/organization/tests/test_organization.py`. Also `app/core/tests/test_health.py`.

Frontend tests (Vitest via `vp test`) are described in [frontend-concept.md](frontend-concept.md).
