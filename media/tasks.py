import importlib.util
import logging

from django.contrib.auth import get_user_model

from media.models import Episode, Title, UserEpisodeState, UserProgress, UserTitleState
from media.services.importer import import_title_by_external_id
from media.services.providers.kinopoisk import KinopoiskProvider
from media.services.user_state import apply_user_state_form, ensure_user_records, toggle_episode_watched

logger = logging.getLogger(__name__)

if importlib.util.find_spec("celery"):
    from celery import shared_task
else:

    def shared_task(func):
        func.delay = func
        return func


@shared_task
def import_title_task(kp_id: int, user_id: int) -> int:
    user = get_user_model().objects.get(pk=user_id)
    provider = KinopoiskProvider()
    title = import_title_by_external_id(kp_id, provider, user)
    logger.info("Импорт завершен user_id=%s title_id=%s", user_id, title.id)
    return title.id


@shared_task
def update_user_title_state_task(user_id: int, title_id: int, status: str, rating, review: str) -> None:
    user = get_user_model().objects.get(pk=user_id)
    title = Title.objects.get(pk=title_id)
    user_state, _ = ensure_user_records(user, title)
    apply_user_state_form(user_state, status=status, rating=rating, review=review)


@shared_task
def toggle_episode_watched_task(user_id: int, episode_id: int, watched: bool) -> None:
    user = get_user_model().objects.get(pk=user_id)
    episode = Episode.objects.select_related("season__title").get(pk=episode_id)
    toggle_episode_watched(user=user, episode=episode, watched=watched)


@shared_task
def remove_from_watchlist_task(user_id: int, title_id: int) -> None:
    UserEpisodeState.objects.filter(user_id=user_id, episode__season__title_id=title_id).delete()
    UserProgress.objects.filter(user_id=user_id, title_id=title_id).delete()
    UserTitleState.objects.filter(user_id=user_id, title_id=title_id).delete()
