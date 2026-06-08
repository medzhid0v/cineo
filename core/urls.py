from django.contrib import admin
from django.urls import include, path, re_path

from media.spa_views import SPAView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("media.api.urls")),
    # Весь фронтенд обслуживает React SPA (клиентский роутинг).
    # Должен идти ПОСЛЕДНИМ, чтобы не перехватывать /admin/ и /api/.
    re_path(r"^.*$", SPAView.as_view(), name="spa"),
]
