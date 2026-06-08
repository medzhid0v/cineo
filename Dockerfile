# ---- Стадия 1: сборка React SPA ----
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# vite build кладёт результат в /app/media/static_spa (см. vite.config outDir)
RUN npm run build


# ---- Стадия 2: Python / Django ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# UID/GID для appuser (фиксированные для совместимости с volume mounts)
ARG UID=1000
ARG GID=1000

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    TZ=Europe/Moscow \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tzdata \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя appuser
RUN groupadd --gid ${GID} appuser \
    && useradd --uid ${UID} --gid ${GID} --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

# Установка таймзоны
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Установка зависимостей
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY --chown=appuser:appuser . .

# Собранный SPA из стадии frontend (исключён из контекста через .dockerignore)
COPY --from=frontend --chown=appuser:appuser /app/media/static_spa /app/media/static_spa

RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app/staticfiles

COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
