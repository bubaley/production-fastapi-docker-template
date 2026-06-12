# ===== Backend =====
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS backend-builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ===== Frontend =====
FROM node:24-alpine AS frontend-builder
WORKDIR /app
RUN corepack enable
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN --mount=type=cache,target=/root/.pnpm-store \
    pnpm install
COPY frontend/ ./
RUN pnpm run build

# ===== Runtime =====
FROM python:3.14-slim-bookworm

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    make \
    ca-certificates \
    curl \
    gnupg \
    caddy \
    # Node.js
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g $GROUP_ID app && useradd -m -u $USER_ID -g app app
WORKDIR /app

COPY --from=backend-builder --chown=app:app /app /app/backend
COPY --from=frontend-builder --chown=app:app /app/.output /app/frontend

COPY --chmod=755 wait-for /usr/local/bin/wait-for
COPY --chown=app:app --chmod=644 Caddyfile /app/Caddyfile
COPY --chown=app:app --chmod=644 Makefile /app/Makefile
COPY --chown=app:app supervisord.conf /etc/supervisor/supervisord.conf

ENV PATH="/app/backend/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENV HOST=0.0.0.0
ENV PORT=3000

USER app
EXPOSE 8080
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
