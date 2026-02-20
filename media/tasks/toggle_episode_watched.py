from celery import shared_task

from media.usecases.toggle_episode_watched import ToggleEpisodeWatchedInput, ToggleEpisodeWatchedUsecase


@shared_task
def toggle_episode_watched_task(user_id: int, episode_id: int, watched: bool) -> None:
    """Переключает статус просмотра эпизода (watched/unwatched) и обновляет прогресс."""
    usecase = ToggleEpisodeWatchedUsecase()
    usecase.execute(
        ToggleEpisodeWatchedInput(
            user_id=user_id,
            episode_id=episode_id,
            watched=watched,
        )
    )
