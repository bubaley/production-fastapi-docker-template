from fastapi import FastAPI

from app.core.database import register_database
from app.domains.project.views import router as project_router
from app.domains.task.views import router as task_router

app = FastAPI(
    title='Production FastAPI Docker Example',
    version='0.0.0',
    description='Production FastAPI Docker Example',
)
register_database(app)

app.include_router(project_router)
app.include_router(task_router)
