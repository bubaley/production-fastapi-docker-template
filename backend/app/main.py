from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_ronin.cache import cache
from pydantic import ValidationError

from app.core.auth import get_auth_state
from app.core.broker import broker
from app.core.database import register_database
from app.core.exceptions import register_exceptions_handlers
from app.core.settings import settings
from app.domains.auth.views import auth_router
from app.domains.organization.services.organization_websocket_service import OrganizationWebSocketService
from app.domains.organization.views import organization_users_router, organizations_router
from app.domains.user.views import user_tokens_router, users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""

    await cache.init(redis_url=settings.cache_redis_url)
    await broker.startup()
    yield
    await broker.shutdown()
    await cache.close()


app = FastAPI(title='fastapi-nuxt-template', version='0.0.0', dependencies=[], lifespan=lifespan)

register_exceptions_handlers(app)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'detail': exc.errors(),
        },
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=['Content-Disposition'],
)


register_database(app)


api_router = APIRouter(prefix='/api/v1', dependencies=[Depends(get_auth_state)])
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(user_tokens_router)
api_router.include_router(organizations_router)
api_router.include_router(organization_users_router)
app.include_router(api_router)


ws_router = APIRouter(prefix='/ws')
OrganizationWebSocketService.register_routes(ws_router)
app.include_router(ws_router)


@app.get('/health')
async def health():
    return {'status': 'ok'}
