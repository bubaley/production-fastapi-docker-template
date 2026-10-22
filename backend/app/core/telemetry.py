import importlib.util
from collections.abc import MutableMapping
from typing import Any

from fastapi.telemetry import TelemetryConfig
from loguru import logger

from app.core.settings import settings

_UNTRACED_PATHS = frozenset({'/health', '/ready'})


def _exclude(scope: MutableMapping[str, Any]) -> bool:
    return scope.get('path') in _UNTRACED_PATHS


def telemetry_config() -> TelemetryConfig:
    """
    FastAPI's native OpenTelemetry. With OTEL_ENABLED=true, OTLP exporters are configured from the standard
    OTEL_* variables (OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME, ...). Requires `uv sync --extra otel`.
    """
    if settings.otel_enabled and importlib.util.find_spec('opentelemetry.sdk') is None:
        logger.warning('OTEL_ENABLED is set but the `otel` extra is not installed; telemetry stays off')
        return {'auto_configure': False, 'exclude': _exclude}
    return {'auto_configure': settings.otel_enabled, 'exclude': _exclude}
