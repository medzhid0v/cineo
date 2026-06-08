from django.conf import settings
from django.http import HttpResponse
from django.views import View


class SPAView(View):
    """
    Отдаёт оболочку React SPA (index.html) для всех фронтенд-маршрутов.

    Ассеты (JS/CSS) отдаёт WhiteNoise по /static/. Клиентский роутинг
    React обрабатывает пути вроде /title/123 — поэтому на любой не-API
    маршрут возвращаем один и тот же index.html.
    """

    _cache: str | None = None

    def get(self, request, *args, **kwargs):
        index = settings.SPA_INDEX
        if not index.exists():
            return HttpResponse(
                "<h1>Cineo</h1><p>Фронтенд не собран. Выполните <code>npm run build</code> "
                "в каталоге <code>frontend/</code> или соберите Docker-образ.</p>",
                status=501,
            )
        # В DEBUG не кэшируем — удобно при пересборке; в проде читаем один раз.
        if settings.DEBUG or SPAView._cache is None:
            SPAView._cache = index.read_text(encoding="utf-8")
        return HttpResponse(SPAView._cache)
