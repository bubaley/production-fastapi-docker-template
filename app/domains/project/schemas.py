from typing import TYPE_CHECKING

from fastapi_mason.schemas import generate_schema, rebuild_schema
from tortoise.contrib.pydantic import PydanticModel

from app.domains.project.meta import ProjectMeta
from app.domains.project.models import Project

ProjectReadSchema = generate_schema(Project, meta=ProjectMeta)
ProjectCreateSchema = rebuild_schema(ProjectReadSchema, exclude_readonly=True)

# Type checking support
if TYPE_CHECKING:
    ProjectReadSchema = type('ProjectReadSchema', (Project, PydanticModel), {})
    ProjectCreateSchema = type('ProjectCreateSchema', (Project, PydanticModel), {})
