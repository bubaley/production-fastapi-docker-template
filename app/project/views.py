from fastapi import APIRouter
from fastapi_mason.decorators import action, viewset

from app.core.viewsets import BaseModelViewSet
from app.project.models import Project
from app.project.schemas import ProjectCreateSchema, ProjectReadSchema

router = APIRouter(prefix='/projects', tags=['projects'])


@viewset(router)
class ProjectViewSet(BaseModelViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema

    @action(methods=['GET'], detail=True, response_model=ProjectReadSchema)
    async def example_route(self, item_id: int):
        obj = await self.get_object(item_id)
        return await ProjectReadSchema.from_tortoise_orm(obj)
