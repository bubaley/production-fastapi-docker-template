from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tortoise.expressions import Q

# A lookup path filtered with `=` (e.g. 'organization__org_users__user_id') or a callable building a Q from the value.
ScopeFilter = str | Callable[[Any], Q]


@dataclass(frozen=True)
class Scope:
    """
    Row-level tenant rule, declared on a model as `tenant_scope`.

    `user` is mandatory and always applied: a row is visible only when it matches the current user.
    `organization`, when set, additionally narrows rows to the organization from the `Organization-Key`
    header. Without that header the request fails, unless `require_organization=False`, in which case
    the user filter alone applies (rows from every organization the user belongs to).
    """

    user: ScopeFilter
    organization: ScopeFilter | None = None
    require_organization: bool = True


@dataclass(frozen=True)
class Unscoped:
    """Explicit opt-out for intentionally global models (reference data). `reason` documents why."""

    reason: str


TenantScope = Scope | Unscoped
