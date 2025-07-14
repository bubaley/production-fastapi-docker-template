from fastapi import Depends, FastAPI

from app.core.auth import get_current_user
from app.core.database import register_database
from app.domains.project.views import projects_router

app = FastAPI(
    title='Production FastAPI Docker Example',
    version='0.0.0',
    description='Production FastAPI Docker Example',
    dependencies=[Depends(get_current_user)],
)
register_database(app)

app.include_router(projects_router)
