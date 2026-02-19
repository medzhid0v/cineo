from celery import shared_task

from media.models import UserEpisodeState, UserProgress, UserTitleState


@shared_task
def remove_from_watchlist_task(user_id: int, title_id: int) -> None:
    """Удаляет тайтл из списка пользователя: все эпизоды, прогресс и статус тайтла."""
    UserEpisodeState.objects.filter(user_id=user_id, episode__season__title_id=title_id).delete()
    UserProgress.objects.filter(user_id=user_id, title_id=title_id).delete()
    UserTitleState.objects.filter(user_id=user_id, title_id=title_id).delete()
