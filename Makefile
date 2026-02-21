PY        := python
MANAGE    := manage.py
UV_RUN    := uv run
DC        := docker compose

.PHONY: run shell mm mig su createsu format lint check fix dev-up dev-down dev-logs docker-up docker-down docker-logs

migrate:
	$(UV_RUN) $(PY) $(MANAGE) migrate

su:
	$(UV_RUN) $(PY) $(MANAGE) createsuperuser

run:
	$(UV_RUN) $(PY) $(MANAGE) runserver 127.0.0.1:8000

run_celery:
	watchfiles "$(UV_RUN) celery -A core worker -l info --pool=solo" .

shell:
	$(UV_RUN) $(PY) $(MANAGE) shell

mm:
	@if [ -n "$(app)" ]; then \
		$(UV_RUN) $(PY) $(MANAGE) makemigrations $(app); \
	else \
		$(UV_RUN) $(PY) $(MANAGE) makemigrations; \
	fi

format:
	ruff format .

lint:
	ruff check .

check:
	ruff format . --check
	ruff check .

fix:
	ruff check . --fix

# Локальная отладка с sqlite
# 1) uv sync
# 2) make mig
# 3) make run

# Запуск локальной docker-инфраструктуры (postgres + redis)
dev-up:
	$(DC) up -d db redis

dev-down:
	$(DC) stop db redis

dev-logs:
	$(DC) logs -f db redis

# Полный запуск приложения в docker (web + celery + flower + postgres + redis)
docker-up:
	$(DC) up --build

docker-down:
	$(DC) down

docker-logs:
	$(DC) logs -f web celery flower db redis
