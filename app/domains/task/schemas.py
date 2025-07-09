from tortoise.contrib.pydantic import pydantic_model_creator

from app.domains.task.models import Task

TaskReadSchema = pydantic_model_creator(Task)
TaskCreateSchema = pydantic_model_creator(Task, exclude_readonly=True)
