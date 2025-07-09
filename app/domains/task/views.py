from fastapi import APIRouter
from fastapi_mason.decorators import viewset

from app.core.viewsets import BaseModelViewSet
from app.domains.task.models import Task
from app.domains.task.schemas import TaskCreateSchema, TaskReadSchema

router = APIRouter(prefix='/tasks', tags=['tasks'])


@viewset(router)
class TaskViewSet(BaseModelViewSet[Task]):
    model = Task
    read_schema = TaskReadSchema
    create_schema = TaskCreateSchema
