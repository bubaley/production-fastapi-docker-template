ifneq (,$(wildcard .env))
	include .env
	export $(shell sed 's/=.*//' .env)
endif

timestamp = $(shell date +"%Y-%m-%d %H:%M:%S.%3N")
log = echo $(call timestamp) $(1)
wait-for = $(call log,"👀$(2) waiting...") && wait-for $(1) && $(call log,"☑️$(2) ready")

GUNICORN_WORKERS ?= 4

# ----------- SHORT COMMANDS ----------- #

r: run ## short run runserver

# ----------- BASE COMMANDS ----------- #

run: ## run runserver
	uvicorn app.main:app --reload

lint: ## run lint
	pre-commit run --all-files

gunicorn: ## run gunicorn
	gunicorn app.main:app --forwarded-allow-ips="*" -k uvicorn.workers.UvicornWorker --timeout=60 --workers=$(GUNICORN_WORKERS) --bind 0.0.0.0:8000

# ----------- PRODUCTION COMMANDS ----------- #

prod-upgrade: ## run upgrade in production
	@$(call wait-for, db:5432, Postgres)

	@$(call log, "🎯 Running migrations...")
	aerich upgrade
	@$(call log, "✅ Migrations completed")

prod-gunicorn: prod-upgrade ## run gunicorn in production
	@$(call log, "🚀 Starting gunicorn...")
	gunicorn app.main:app --forwarded-allow-ips="*" -k uvicorn.workers.UvicornWorker --timeout=60 --workers=$(GUNICORN_WORKERS) --bind 0.0.0.0:8000 --preload --max-requests 1000 --max-requests-jitter 50

# ----------- HELPERS ----------- #

help:
	@echo "Usage: make <target>"
	@awk 'BEGIN {FS = ":.*##"} /^[0-9a-zA-Z_-]+:.*?## / { printf "  * %-20s -%s\n", $$1, $$2 }' $(MAKEFILE_LIST)
