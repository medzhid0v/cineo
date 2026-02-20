# Cineo

![Cineo](docs/demo.gif)

**Cineo** — локальное self-host приложение для персональной фильмотеки. Хранит фильмы и метаданные исключительно локально, без облаков.

## Возможности

- Организация и каталогизация локальных фильмов
- Управление коллекцией через веб-интерфейс
- Полностью офлайн, приватность и контроль данных

## Быстрый старт
### Docker

```
cp .env.example .env
```

```bash
docker compose up --build
```

```bash
docker compose exec web python manage.py createsuperuser
```

**Сервисы:**
- Приложение: `http://localhost:8080`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
