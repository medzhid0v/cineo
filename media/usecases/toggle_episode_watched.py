from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction

from media.models import Episode, UserEpisodeState
from media.services.user_state import toggle_episode_watched
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class ToggleEpisodeWatchedInput:
    user_id: int
    episode_id: int
    watched: bool


class ToggleEpisodeWatchedUsecase(BaseUsecase[ToggleEpisodeWatchedInput, UserEpisodeState]):
    """Usecase для переключения статуса просмотра эпизода."""

    @transaction.atomic
    def execute(self, data: ToggleEpisodeWatchedInput) -> UserEpisodeState:
        user = get_user_model().objects.get(pk=data.user_id)
        episode = Episode.objects.select_related("season__title").get(pk=data.episode_id)
        return toggle_episode_watched(user=user, episode=episode, watched=data.watched)
