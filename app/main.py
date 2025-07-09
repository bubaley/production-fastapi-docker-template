from fastapi import FastAPI

from app.core.database import register_database
from app.project.views import router as project_router

app = FastAPI(
    title='Production FastAPI Docker Example',
    version='0.0.0',
    description='Production FastAPI Docker Example',
)
register_database(app)

app.include_router(project_router)
