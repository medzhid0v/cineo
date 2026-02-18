# Сineo

**Cineo** — это локальное **self-host** приложение для персональной фильмотеки.
Каждый пользователь разворачивает Cineo у себя на компьютере или сервере и хранит фильмы исключительно локально, без облаков и сторонних сервисов.

### **Cineo** позволяет:
- организовывать и каталогизировать локальные фильмы
- хранить метаданные и обложки рядом с файлами
- просматривать и управлять коллекцией через удобный интерфейс
- работать полностью офлайн, с упором на приватность и контроль данных

## Локальный запуск (sqlite)
```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

## Docker запуск (web + celery + flower + postgres + redis)
```bash
cp .env.example .env
docker compose up --build
```

Сервисы:
- Приложение: `http://localhost:8000`
- Flower: `http://localhost:5555`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
