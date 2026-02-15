from django.urls import path

from .views import ImportView, TitleDetailView, TitleListView

app_name = "media"

urlpatterns = [
    path("", TitleListView.as_view(), name="list"),
    path("import/", ImportView.as_view(), name="import"),
    path("title/<int:pk>/", TitleDetailView.as_view(), name="detail"),
]
