ifneq (,$(wildcard .env))
	include .env
	export $(shell sed 's/=.*//' .env)
endif

UV := uv
PNPM := pnpm

BACKEND_DIR := backend
FRONTEND_DIR := frontend

BACKEND_APP := app.main:app
BACKEND_HOST ?= 0.0.0.0
BACKEND_PORT ?= 8000
FRONTEND_HOST ?= 0.0.0.0
FRONTEND_PORT ?= 8080

TASKIQ_WORKERS ?= 1
TASKIQ_UPDATE_INTERVAL ?= 10

GUNICORN_WORKERS ?= 1

# ----------- SHORT COMMANDS ----------- #

rb: run-backend ## short run backend api
rf: run-frontend ## short run frontend dev
rt: run-taskiq ## short run taskiq

mm: make-migrations ## short run make migrations
m: migrate ## short run migrate
t: test ## short run backend tests

# ----------- SETUP ----------- #

install: install-backend install-frontend ## install all dependencies

install-backend: ## install backend dependencies via uv
	$(UV) sync --project $(BACKEND_DIR) --locked

install-frontend: ## install frontend dependencies via pnpm
	$(PNPM) --dir $(FRONTEND_DIR) install

make-migrations: ## run migrations
	cd $(BACKEND_DIR) && tortoise makemigrations

migrate: ## run migrations
	cd $(BACKEND_DIR) && tortoise migrate

prepare: ## prepare project
	cd $(FRONTEND_DIR) && pnpm nuxt prepare

# ----------- DEVELOPMENT ----------- #

run-backend: ## run FastAPI with reload
	cd $(BACKEND_DIR) && uvicorn $(BACKEND_APP) --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

run-frontend: ## run Nuxt dev server
	cd $(FRONTEND_DIR) && pnpm dev --port $(FRONTEND_PORT)

run-taskiq: ## Run both scheduler and worker
	$(MAKE) -j2 run-taskiq-scheduler run-taskiq-worker

run-taskiq-worker: ## Run taskiq worker
	cd $(BACKEND_DIR) && python -m taskiq worker app.core.broker:broker --fs-discover --tasks-pattern "app/**/tasks.py" --workers $(TASKIQ_WORKERS)

run-taskiq-scheduler: ## Run taskiq scheduler
	cd $(BACKEND_DIR) && python -m taskiq scheduler app.core.broker:scheduler --fs-discover --tasks-pattern "app/**/tasks.py" --update-interval $(TASKIQ_UPDATE_INTERVAL)

test: test-backend ## run backend tests

test-backend: ## run backend pytest suite
	cd $(BACKEND_DIR) && uv run manage.py test

# ----------- PRODUCTION ----------- #

run-prod-backend: ## run backend API in prod mode
	cd $(BACKEND_DIR) && python -m gunicorn app.main:app --bind 0.0.0.0:8000 --workers $(GUNICORN_WORKERS) -k uvicorn.workers.UvicornWorker --timeout 120

run-prod-frontend: ## run built frontend SSR server
	node $(FRONTEND_DIR)/server/index.mjs

run-prod-taskiq: ## run taskiq worker in backend context
	$(MAKE) run-taskiq

run-prod-caddy: ## run caddy reverse proxy
	caddy run --config Caddyfile

# ----------- QUALITY ----------- #

lint: lint-backend lint-frontend ## lint backend+frontend

lint-backend: ## run backend checks (ruff)
	cd $(BACKEND_DIR) && pre-commit run --all-files

lint-frontend: ## run frontend lint
	$(PNPM) --dir $(FRONTEND_DIR) exec eslint . --fix

# ----------- HELPERS ----------- #

help:
	@echo "Usage: make <target>"
	@awk 'BEGIN {FS = ":.*##"} /^[0-9a-zA-Z_-]+:.*?## / { printf "  * %-20s - %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
