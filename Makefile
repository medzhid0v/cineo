# Makefile for local Django development with uv

PY        := python
MANAGE    := manage.py
UV_RUN    := uv run

.PHONY: help venv install init run shell mm mig showm su createsu dbreset check test

run:
	$(UV_RUN) $(PY) $(MANAGE) runserver 127.0.0.1:8000

shell:
	$(UV_RUN) $(PY) $(MANAGE) shell

# makemigrations; usage: make mm (all apps) OR make mm app=media
mm:
	@if [ -n "$(app)" ]; then \
		$(UV_RUN) $(PY) $(MANAGE) makemigrations $(app); \
	else \
		$(UV_RUN) $(PY) $(MANAGE) makemigrations; \
	fi

mig:
	$(UV_RUN) $(PY) $(MANAGE) migrate

su:
	$(UV_RUN) $(PY) $(MANAGE) createsuperuser

createsu: su