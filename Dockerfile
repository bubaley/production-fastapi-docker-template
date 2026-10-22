# syntax=docker/dockerfile:1
#
# One image: Caddy (:8080) in front of FastAPI (127.0.0.1:8000) and Nuxt (127.0.0.1:3000),
# plus the Taskiq worker and scheduler, supervised by s6-overlay. See docs/deployment.md.

# Base images, pinned here once (Dependabot updates these FROM lines). Builder and runtime share
# the Python image so the venv's interpreter path matches; Node (builder and the copied binary)
# uses the same Debian release, so the same glibc, as the runtime.
FROM python:3.14.9-slim-trixie AS python
FROM node:26.11.1-trixie-slim AS node
FROM caddy:2.11.7-alpine AS caddy
FROM ghcr.io/astral-sh/uv:0.13.5 AS uv

# ===== s6-overlay: downloaded and checksum-verified in a throwaway stage =====
FROM debian:trixie-slim AS s6
ARG S6_OVERLAY_VERSION=3.2.3.2
ARG S6_NOARCH_SHA256=5379750ed30a84bbd2e2dd74847ba6b5bd29cd0b2e3ea2ec58049b57eb2eda12
ARG S6_X86_64_SHA256=e6befcc96a437a3831386ecfc51808c5d3e939dc5fe3c02ae9284599e8aa2408
ARG S6_AARCH64_SHA256=b17f17a82e7a515c682a91edaf2ffdabb73f891981b6c1fd712115693a2f8b4c
ARG TARGETARCH
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl xz-utils \
    && rm -rf /var/lib/apt/lists/*
RUN set -eu; \
    case "${TARGETARCH:-amd64}" in \
      amd64) arch=x86_64; sum="${S6_X86_64_SHA256}" ;; \
      arm64) arch=aarch64; sum="${S6_AARCH64_SHA256}" ;; \
      *) echo "unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    base="https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}"; \
    curl -fsSLo /tmp/noarch.tar.xz "${base}/s6-overlay-noarch.tar.xz"; \
    curl -fsSLo /tmp/arch.tar.xz "${base}/s6-overlay-${arch}.tar.xz"; \
    printf '%s  %s\n%s  %s\n' "${S6_NOARCH_SHA256}" /tmp/noarch.tar.xz "${sum}" /tmp/arch.tar.xz | sha256sum -c -; \
    mkdir -p /s6-root; \
    tar -C /s6-root -Jxpf /tmp/noarch.tar.xz; \
    tar -C /s6-root -Jxpf /tmp/arch.tar.xz

# ===== Backend: locked production dependencies in /app/backend/.venv =====
FROM python AS backend-builder
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/backend/.venv
WORKDIR /app/backend
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev \
    && .venv/bin/python -m compileall -q app

# ===== Frontend: Nuxt build output in /app/frontend/.output =====
FROM node AS frontend-builder
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    NUXT_TELEMETRY_DISABLED=1
RUN corepack enable
WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm fetch --frozen-lockfile --store-dir /pnpm/store
COPY frontend/ ./
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile --offline --store-dir /pnpm/store \
    && pnpm run build

# ===== Runtime =====
FROM python AS runtime

ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd --system --gid "${APP_GID}" app \
    && useradd --system --uid "${APP_UID}" --gid app --home-dir /home/app --create-home --shell /usr/sbin/nologin app

COPY --from=s6 /s6-root/ /
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=caddy /usr/bin/caddy /usr/local/bin/caddy

# Node needs only glibc and libstdc++, both in the slim Python image; fail the build if that changes.
# s6-overlay runs as the unprivileged user: /run holds its supervision tree.
RUN node --version && caddy version \
    && chown app:app /run

COPY --from=backend-builder /app/backend /app/backend
COPY --from=frontend-builder /app/frontend/.output /app/frontend/.output
COPY Caddyfile /etc/caddy/Caddyfile
COPY docker/rootfs/ /

ENV PATH="/app/backend/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    LOG_FORMAT=json \
    XDG_CONFIG_HOME=/tmp/xdg/config \
    XDG_DATA_HOME=/tmp/xdg/data \
    # s6-overlay: stop the container when migrate fails or a service dies (see finish scripts),
    # and give services time for graceful shutdown (uvicorn and Caddy wait up to 20s).
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
    S6_SERVICES_GRACETIME=25000 \
    S6_KILL_GRACETIME=3000 \
    S6_VERBOSITY=1

WORKDIR /app
USER app
EXPOSE 8080
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --start-interval=2s --retries=3 \
    CMD ["/usr/local/bin/python3", "-I", "/usr/local/bin/healthcheck"]

ENTRYPOINT ["/init"]

# Last, so a new version does not invalidate the layers above.
ARG APP_VERSION=0.0.0-dev
ARG GIT_SHA=unknown
ARG BUILD_DATE
ENV APP_VERSION=${APP_VERSION} \
    GIT_SHA=${GIT_SHA}
LABEL org.opencontainers.image.title="fastapi-nuxt-template" \
      org.opencontainers.image.description="FastAPI + Nuxt application behind Caddy, supervised by s6-overlay" \
      org.opencontainers.image.source="https://github.com/bubaley/production-fastapi-docker-template" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}"
