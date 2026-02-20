from dataclasses import dataclass

from django.db import transaction

from media.models import UserEpisodeState, UserProgress, UserTitleState
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class RemoveFromWatchlistInput:
    user_id: int
    title_id: int


class RemoveFromWatchlistUsecase(BaseUsecase[RemoveFromWatchlistInput, None]):
    """Usecase для удаления тайтла из списка пользователя."""

    @transaction.atomic
    def execute(self, data: RemoveFromWatchlistInput) -> None:
        """Удаляет все эпизоды, прогресс и статус тайтла для пользователя."""
        UserEpisodeState.objects.filter(user_id=data.user_id, episode__season__title_id=data.title_id).delete()
        UserProgress.objects.filter(user_id=data.user_id, title_id=data.title_id).delete()
        UserTitleState.objects.filter(user_id=data.user_id, title_id=data.title_id).delete()
