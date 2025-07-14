from fastapi import APIRouter
from fastapi_mason.decorators import viewset

from app.core.viewsets import BaseViewSet
from app.domains.project.models import Project
from app.domains.project.schemas import (
    ProjectCreateSchema,
    ProjectReadSchema,
)

projects_router = APIRouter(prefix='/projects', tags=['projects'])


@viewset(projects_router)
class ProjectViewSet(BaseViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema
