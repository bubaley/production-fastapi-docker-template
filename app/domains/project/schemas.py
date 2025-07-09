from tortoise.contrib.pydantic import pydantic_model_creator

from app.domains.project.models import Project

ProjectReadSchema = pydantic_model_creator(Project)
ProjectCreateSchema = pydantic_model_creator(Project, exclude_readonly=True)
