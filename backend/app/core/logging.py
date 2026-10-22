import json
import logging
import sys
import traceback
from typing import Any

from loguru import logger

from app.core.request_id import get_request_id
from app.core.settings import settings

# Standard-library loggers routed through loguru (uvicorn access/error logs included).
_INTERCEPTED_LOGGERS = ('uvicorn', 'uvicorn.error', 'uvicorn.access', 'fastapi', 'taskiq', 'tortoise', 'asyncio')

_TEXT_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | '
    '<magenta>{extra[request_id]}</magenta> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>'
)


class InterceptHandler(logging.Handler):
    """Forward standard-library log records to loguru, keeping the caller location."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _bind_request_id(record: Any) -> None:
    record['extra'].setdefault('request_id', get_request_id() or '-')


def _json_sink(message: Any) -> None:
    record = message.record
    extra = {key: value for key, value in record['extra'].items() if key != 'request_id'}
    payload: dict[str, Any] = {
        'time': record['time'].isoformat(),
        'level': record['level'].name,
        'message': record['message'],
        'logger': record['name'],
        'function': record['function'],
        'line': record['line'],
        'request_id': record['extra'].get('request_id'),
    }
    if extra:
        payload['extra'] = extra
    if record['exception'] is not None:
        exc_type, exc_value, exc_tb = record['exception']
        payload['exception'] = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    sys.stdout.write(json.dumps(payload, default=str, ensure_ascii=False) + '\n')
    sys.stdout.flush()


def setup_logging() -> None:
    """Configure loguru as the only log sink. Idempotent; call once per process (API and taskiq worker)."""
    logger.remove()
    logger.configure(patcher=_bind_request_id)
    if settings.log_format == 'json':
        logger.add(_json_sink, level=settings.log_level, backtrace=False, diagnose=False)
    else:
        logger.add(sys.stdout, level=settings.log_level, format=_TEXT_FORMAT, backtrace=False, diagnose=False)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in _INTERCEPTED_LOGGERS:
        std_logger = logging.getLogger(name)
        std_logger.handlers = []
        std_logger.propagate = True
