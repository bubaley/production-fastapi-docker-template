from tortoise import fields

from app.core.models import BaseModel
from app.domains.project.models import Project


class Task(BaseModel):
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField('models.Project', related_name='tasks')
