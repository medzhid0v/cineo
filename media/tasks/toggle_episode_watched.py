from celery import shared_task
from django.contrib.auth import get_user_model

from media.models import Episode
from media.services.user_state import toggle_episode_watched


@shared_task
def toggle_episode_watched_task(user_id: int, episode_id: int, watched: bool) -> None:
    """Переключает статус просмотра эпизода (watched/unwatched) и обновляет прогресс."""
    user = get_user_model().objects.get(pk=user_id)
    episode = Episode.objects.select_related("season__title").get(pk=episode_id)
    toggle_episode_watched(user=user, episode=episode, watched=watched)
