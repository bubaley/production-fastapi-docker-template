from tortoise import fields

from app.core.models import BaseModel


class Project(BaseModel):
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
