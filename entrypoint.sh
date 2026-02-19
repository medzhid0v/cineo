#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

# Получаем параметры подключения из переменных окружения
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-cineo}"
POSTGRES_USER="${POSTGRES_USER:-cineo}"

# Ждем готовности PostgreSQL
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"

# Применяем миграции
uv run python manage.py migrate --noinput

# Собираем статику только если это web сервис (определяем по команде)
if echo "$@" | grep -q "runserver\|gunicorn\|uwsgi"; then
  echo "Collecting static files..."
  uv run python manage.py collectstatic --noinput || true
fi

echo "Starting command: $@"
exec "$@"
