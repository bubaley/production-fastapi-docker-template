"""
FastAPI Logger Service

This module provides structured JSON logging for FastAPI applications.

Usage example:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.base import BaseHTTPMiddleware
import uuid

from app.core.services.logger import Logg, set_request_context, init_logging

app = FastAPI()

# Initialize logging
logging_config = init_logging(Path("./logs"), debug=True)
logging.config.dictConfig(logging_config)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        set_request_context(
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            user_id=getattr(request.state, 'user_id', None)  # If you have auth
        )

        Logg.info(e='request.start', msg=f'Starting {request.method} {request.url.path}')

        try:
            response = await call_next(request)
            Logg.info(e='request.end', status_code=response.status_code)
            return response
        except Exception as e:
            Logg.error(e='request.error', error=str(e))
            raise

app.add_middleware(RequestLoggingMiddleware)

# Usage in your code
Logg.info(e='user.created', user_id='123', email='user@example.com')
Logg.error(e='payment.failed', amount=100.50, reason='insufficient_funds')
```
"""

import inspect
import json
import logging
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Callable, Literal, Optional

from loguru import logger

request_context_var = ContextVar('request_context')

CRITICAL = 'CRITICAL'
ERROR = 'ERROR'
WARNING = 'WARNING'
INFO = 'INFO'
DEBUG = 'DEBUG'

LOG_LEVEL = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    method: Optional[str] = None,
    url: Optional[str] = None,
    **kwargs,
):
    """Set context variables for the current request in FastAPI."""
    context = {}
    if request_id:
        context['request_id'] = request_id
    if user_id:
        context['user_id'] = user_id
    if method:
        context['method'] = method
    if url:
        context['url'] = url
    context.update(kwargs)
    request_context_var.set(context)


def get_request_context() -> dict:
    """Get current request context."""
    try:
        return request_context_var.get()
    except LookupError:
        return {}


class Logg:
    """Class for logging events in JSON format.

    Arguments::
        args : don't use unnamed arguments
        e : indicate the event with a dot
        msg : always set by the second argument. Use short string

    Usage::
        Logg.info(e='balance.updated', msg='guest balance increased', sum=322)
    """

    @staticmethod
    def info(*args, **kwargs):
        Logg._log(INFO, *args, **kwargs)

    @staticmethod
    def warning(*args, **kwargs):
        Logg._log(WARNING, *args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        Logg._log(ERROR, *args, **kwargs)

    @staticmethod
    def debug(*args, **kwargs):
        Logg._log(DEBUG, *args, **kwargs)

    @staticmethod
    def critical(*args, **kwargs):
        Logg._log(CRITICAL, *args, **kwargs)

    @staticmethod
    def log(level: LOG_LEVEL, *args, **kwargs):
        Logg._log(level, *args, **kwargs)

    @staticmethod
    def _log(level: LOG_LEVEL, *args, **kwargs):
        message = Logg._generate_message(*args, **kwargs)
        logger.opt(depth=2).log(level, message)

    @staticmethod
    def _generate_message(*args, **kwargs):
        kwargs = kwargs.copy()
        kwargs = Logg._process_request_context(kwargs)
        data: dict = {'e': str(kwargs.pop('e')).lower() if 'e' in kwargs else 'message'}
        if len(args) > 0 and isinstance(args[0], str) and 'msg' not in kwargs:
            data['msg'] = args[0]
            args = args[1:]
        elif 'msg' in kwargs:
            data['msg'] = str(kwargs.pop('msg'))
        data.update(kwargs)
        if args:
            data['args'] = args
        return json.dumps(data, default=str, ensure_ascii=False)

    @staticmethod
    def _process_request_context(kwargs: dict):
        try:
            request_context_data: dict = request_context_var.get()
            for key, value in request_context_data.items():
                if key not in kwargs:
                    kwargs[key] = value
            return kwargs
        except Exception:
            return kwargs


def init_logging(log_dir: Path, debug: bool, *args, **kwargs):
    _init_logger(log_dir, debug, *args, **kwargs)
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': INFO,
                'class': logging.StreamHandler,
            },
            'loguru': {
                'level': INFO,
                'class': LoguruHandler,
            },
        },
        'loggers': {
            'uvicorn': {
                'handlers': ['loguru'],
                'level': INFO,
                'propagate': False,
            },
            'uvicorn.access': {
                'handlers': ['loguru'],
                'level': INFO,
                'propagate': False,
            },
            'fastapi': {
                'handlers': ['loguru'],
                'level': INFO,
                'propagate': False,
            },
        },
    }


def _init_logger(log_dir: Path, debug: bool, *args, **kwargs):
    sys.excepthook = _log_exceptions

    format_values = [
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>',
        '<level>{level: <8}</level>',
        '{message}',
        '<cyan>{name}<red>:</red>{function}<red>:</red>{line}</cyan>',
    ]
    params = {'format': ' <red>|</red> '.join(format_values), 'backtrace': False, 'diagnose': False}

    logger.remove()
    logger.add(
        sys.stdout,
        **params,
    )


def _log_exceptions(exc_type, exc_value, exc_traceback):
    message = Logg._generate_message(e='exception.hook', type=exc_type.__name__)
    logger.opt(exception=exc_value).log(ERROR, message)


class LoguruHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        message = self._prepare_message(record)
        depth = self._get_depth(record)
        logger.opt(exception=record.exc_info, depth=depth).log(level, message)

    @staticmethod
    def _get_depth(record: logging.LogRecord):
        for depth, frame in enumerate(inspect.stack()):
            if record.pathname == frame.filename:
                return depth - 1
        return 2

    @staticmethod
    def _prepare_message(record: logging.LogRecord):
        # Handle FastAPI/uvicorn logs
        if record.name.startswith(('uvicorn', 'fastapi')):
            return Logg._generate_message(e='fastapi.trace', msg=record.getMessage())
        else:
            return Logg._generate_message(e='app.trace', msg=record.getMessage())


type LoggProxyContext = dict | Callable[..., dict] | None


class LoggProxy:
    def __init__(
        self,
        *,
        prefix: str | None = None,
        context: LoggProxyContext = None,
        disable_context_update: bool = False,
    ):
        self.prefix = prefix
        self._context = context or {}
        self.disable_context_update = disable_context_update
        self._logger = Logg

    @property
    def context(self):
        if callable(self._context):
            return self._context() or {}
        return self._context or {}

    def info(self, *args, **kwargs):
        self._log(INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self._log(WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._log(ERROR, *args, **kwargs)

    def debug(self, *args, **kwargs):
        self._log(DEBUG, *args, **kwargs)

    def critical(self, *args, **kwargs):
        self._log(CRITICAL, *args, **kwargs)

    def log(self, level: LOG_LEVEL, *args, **kwargs):
        self._log(level, *args, **kwargs)

    def update_context(self, context: LoggProxyContext, replace: bool = False):
        context = context or {}
        if replace or callable(context):
            self._context = context if callable(context) else context.copy()
        elif isinstance(self._context, dict):
            self._context.update(context)

    def _log(self, level: LOG_LEVEL, *args, **kwargs):
        kwargs = self._process_kwargs(kwargs)
        self._logger._log(level, *args, **kwargs)

    def _process_kwargs(self, kwargs: dict):
        event_key = 'e'
        merged = self.context.copy()

        event_prefix = self.prefix or ''
        original_event = kwargs.get(event_key, None)
        if original_event:
            if event_prefix:
                event_prefix += '.'
            event_prefix += original_event
        merged[event_key] = event_prefix
        for k, v in kwargs.items():
            if k == event_key:
                continue
            merged[k] = v
            if not self.disable_context_update and k in self.context:
                self.context[k] = v
        return merged
