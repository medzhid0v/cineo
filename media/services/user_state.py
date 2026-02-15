from django.db import transaction
from django.utils import timezone

from media.models import Episode, Title, UserEpisodeState, UserProgress, UserTitleState, WatchStatus


@transaction.atomic
def ensure_user_records(user, title: Title):
    user_state, _ = UserTitleState.objects.get_or_create(user=user, title=title)
    progress, _ = UserProgress.objects.get_or_create(user=user, title=title)
    return user_state, progress


@transaction.atomic
def apply_user_state_form(user_state: UserTitleState, *, status: str, rating, review: str) -> UserTitleState:
    user_state.status = status
    user_state.rating = rating
    user_state.review = review

    today = timezone.localdate()
    if status == WatchStatus.WATCHING and not user_state.started_at:
        user_state.started_at = today
    if status == WatchStatus.COMPLETED and not user_state.finished_at:
        user_state.finished_at = today

    user_state.save(update_fields=["status", "rating", "review", "started_at", "finished_at", "updated_at"])
    return user_state


@transaction.atomic
def toggle_episode_watched(*, user, episode: Episode, watched: bool) -> UserEpisodeState:
    state, _ = UserEpisodeState.objects.get_or_create(user=user, episode=episode)
    state.watched = watched
    state.watched_at = timezone.now() if watched else None
    state.save(update_fields=["watched", "watched_at"])

    title = episode.season.title
    progress, _ = UserProgress.objects.get_or_create(user=user, title=title)

    last_watched = (
        UserEpisodeState.objects.filter(user=user, watched=True, episode__season__title=title)
        .select_related("episode__season")
        .order_by("episode__season__number", "episode__number")
        .last()
    )

    if last_watched:
        progress.current_season_number = last_watched.episode.season.number
        progress.current_episode_number = last_watched.episode.number
        progress.last_watched_at = timezone.now()
    else:
        progress.current_season_number = None
        progress.current_episode_number = None
        progress.last_watched_at = None

    progress.save(update_fields=["current_season_number", "current_episode_number", "last_watched_at"])
    return state
