from dataclasses import dataclass

from django.contrib.auth import get_user_model

from media.models import Episode, Title, UserEpisodeState, UserProgress, UserTitleState
from media.services.user_state import ensure_user_records
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class GetTitleDetailInput:
    user_id: int
    title_id: int


@dataclass(frozen=True)
class GetTitleDetailOutput:
    title: Title
    user_state: UserTitleState
    progress: UserProgress
    watched_episode_ids: set[int]
    total_episodes: int
    watched_episodes: int


class GetTitleDetailUsecase(BaseUsecase[GetTitleDetailInput, GetTitleDetailOutput]):
    """Usecase для получения детальной информации о тайтле с данными пользователя."""

    def execute(self, data: GetTitleDetailInput) -> GetTitleDetailOutput:
        user = get_user_model().objects.get(pk=data.user_id)
        title = Title.objects.prefetch_related("seasons__episodes").get(pk=data.title_id)

        user_state, progress = ensure_user_records(user, title)

        watched_states = UserEpisodeState.objects.filter(
            user_id=data.user_id,
            episode__season__title=title,
            watched=True,
        ).select_related("episode")
        watched_ids = set(watched_states.values_list("episode_id", flat=True))

        episodes_qs = Episode.objects.filter(season__title=title)
        total_episodes = episodes_qs.count()
        watched_episodes = len(watched_ids)

        return GetTitleDetailOutput(
            title=title,
            user_state=user_state,
            progress=progress,
            watched_episode_ids=watched_ids,
            total_episodes=total_episodes,
            watched_episodes=watched_episodes,
        )
