#!/bin/sh
set -e

# Определяем тип сервиса по команде
COMMAND="$1"

init_web() {
    echo "Initializing web service..."

    # Применяем миграции (от appuser через gosu)
    # Для миграций нужно прямое подключение к БД, временно отключаем PgBouncer
    echo "Running migrations (direct PostgreSQL connection)..."
    gosu appuser python3 manage.py migrate

    # Собираем статику
    gosu appuser python3 manage.py collectstatic --no-input --clear -v 0
}

init_celery() {
    echo "Initializing celery worker..."
    # Ждём готовности Django
    gosu appuser python3 -c "import django; django.setup()" 2>/dev/null || sleep 5
}

# Выбираем инициализацию в зависимости от команды
case "$COMMAND" in
    python3|python|gunicorn|uwsgi)
        init_web
        ;;
    celery)
        init_celery
        ;;
    *)
        echo "Running command: $@"
        ;;
esac

# Запускаем основной процесс от appuser
exec gosu appuser "$@"
