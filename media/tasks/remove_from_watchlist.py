from celery import shared_task

from media.usecases.remove_from_watchlist import RemoveFromWatchlistInput, RemoveFromWatchlistUsecase


@shared_task
def remove_from_watchlist_task(user_id: int, title_id: int) -> None:
    """Удаляет тайтл из списка пользователя: все эпизоды, прогресс и статус тайтла."""
    usecase = RemoveFromWatchlistUsecase()
    usecase.execute(
        RemoveFromWatchlistInput(
            user_id=user_id,
            title_id=title_id,
        )
    )
