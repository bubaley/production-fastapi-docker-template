from fastapi_mason.schemas import SchemaMeta

from app.core.models import BASE_FIELDS


class ProjectMeta(SchemaMeta):
    include = (
        *BASE_FIELDS,
        'name',
        'description',
    )
