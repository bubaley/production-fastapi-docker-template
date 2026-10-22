from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.types import ASGIApp

from app.core.auth import get_auth_state
from app.core.broker import broker
from app.core.database import register_database
from app.core.exceptions import register_exceptions_handlers
from app.core.health import health_router
from app.core.logging import setup_logging
from app.core.redis import close_redis
from app.core.request_id import REQUEST_ID_HEADER, RequestIdMiddleware
from app.core.services.websocket_service import start_websocket_fanout, stop_websocket_fanout
from app.core.settings import settings
from app.core.telemetry import telemetry_config
from app.domains.auth.views import auth_router
from app.domains.organization.services.organization_websocket_service import OrganizationWebSocketService
from app.domains.organization.views import organization_users_router, organizations_router
from app.domains.user.views import user_tokens_router, users_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start optional dependencies without making them boot requirements; always release what started."""
    async with AsyncExitStack() as stack:
        stack.push_async_callback(close_redis)
        try:
            await broker.startup()
            stack.push_async_callback(broker.shutdown)
        except Exception as e:
            logger.warning('Task broker unavailable at startup ({}); /ready reports Redis', e)
        await start_websocket_fanout()
        stack.push_async_callback(stop_websocket_fanout)
        logger.info('Application started: version {} ({})', settings.app_version, settings.git_sha or 'no sha')
        yield


class App(FastAPI):
    def build_middleware_stack(self) -> ASGIApp:
        # Outside Starlette's error middleware, so unhandled errors are logged with the request id.
        return RequestIdMiddleware(super().build_middleware_stack())


app = App(
    title='fastapi-nuxt-template',
    version=settings.app_version,
    lifespan=lifespan,
    telemetry=telemetry_config(),
)

register_exceptions_handlers(app)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=['Content-Disposition', REQUEST_ID_HEADER],
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

app.include_router(health_router)
