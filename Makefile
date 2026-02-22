# =========================
# Base commands / variables
# =========================

PY        := python
MANAGE    := manage.py
UV_RUN    := uv run
DC        := docker compose
DC_DEV    := docker compose -f docker-compose.dev.yml

# =========================
# Env loading (DEV)
# =========================
# Переменные из .env подгружаем снаружи через python-dotenv CLI.
#
# Пример ручного запуска:
#   uv run dotenv -f .env run -- python manage.py runserver

DOTENV_FILE ?= .env
DOTENV_RUN  := $(UV_RUN) dotenv -f $(DOTENV_FILE) run --

# =========================
# Targets
# =========================

.PHONY: \
	dev-run dev-celery-run dev-makemig dev-migrate dev-createsu \
	format lint check fix lint_all \
	dev-docker-up dev-docker-down dev-docker-logs \
	docker-up docker-down docker-logs


# =========================
# Django (DEV) - local runserver/management via dotenv
# =========================

dev-migrate:
	$(DOTENV_RUN) $(UV_RUN) $(PY) $(MANAGE) migrate

dev-createsu:
	$(DOTENV_RUN) $(UV_RUN) $(PY) $(MANAGE) createsuperuser

dev-run:
	$(DOTENV_RUN) $(UV_RUN) $(PY) $(MANAGE) runserver 127.0.0.1:8000

dev-makemig:
	@if [ -n "$(app)" ]; then \
		$(DOTENV_RUN) $(UV_RUN) $(PY) $(MANAGE) makemigrations $(app); \
	else \
		$(DOTENV_RUN) $(UV_RUN) $(PY) $(MANAGE) makemigrations; \
	fi


# =========================
# Celery (DEV) - auto-reload worker
# =========================
# watchfiles перезапускает worker при изменениях в проекте.

dev-celery-run:
	$(DOTENV_RUN) watchfiles "$(UV_RUN) celery -A core worker -l info --pool=solo" .


# =========================
# Code quality (local)
# =========================
# Ruff берёт настройки из pyproject.toml

format:
	$(UV_RUN) ruff format .

lint:
	$(UV_RUN) ruff check .

check:
	$(UV_RUN) ruff format . --check
	$(UV_RUN) ruff check .

fix:
	$(UV_RUN) ruff check . --fix

lint_all:
	pre-commit run --all-files

# =========================
# Docker infra (DEV) - only Postgres + Redis
# =========================

dev-docker-up:
	$(DC_DEV) up -d postgres redis

dev-docker-down:
	$(DC_DEV) down postgres redis

dev-docker-logs:
	$(DC_DEV) logs -f postgres redis


# =========================
# Docker full stack (PROD-like) - build and run everything
# =========================

docker-up:
	$(DC) up --build

docker-down:
	$(DC) down

docker-logs:
	$(DC) logs -f web celery
