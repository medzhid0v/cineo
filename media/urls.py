from django.urls import path

from .views import (
    ReceiveTitleView,
    RemoveFromWatchlistView,
    TitleDetailView,
    TitleListView,
    ToggleEpisodeWatchedView,
    UpdateUserTitleStateView,
)

app_name = "media"

urlpatterns = [
    path("", TitleListView.as_view(), name="list"),
    path("import/", ReceiveTitleView.as_view(), name="import"),
    path("title/<int:pk>/", TitleDetailView.as_view(), name="detail"),
    path("title/<int:pk>/state/", UpdateUserTitleStateView.as_view(), name="update_state"),
    path("title/<int:pk>/episode/<int:episode_id>/toggle/", ToggleEpisodeWatchedView.as_view(), name="toggle_episode"),
    path("title/<int:pk>/remove/", RemoveFromWatchlistView.as_view(), name="remove"),
]
