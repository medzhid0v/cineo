from dataclasses import dataclass
from typing import Any

from media.dtos import SeasonsDTO
from media.services.providers.factory import ProviderFactory
from media.services.title_receiver import update_or_create_title
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class ReceiveTitleInput:
    user_id: int
    source_id: int


class ReceiveTitleUsecase(BaseUsecase[ReceiveTitleInput, dict[str, Any]]):
    def execute(
        self,
        data: ReceiveTitleInput,
    ) -> dict[str, Any]:
        provider = ProviderFactory.init_provider("kinopoisk")

        title_dto = provider.get_title(external_id=data.source_id)

        seasons_dto = SeasonsDTO()
        if title_dto.is_series:
            seasons_dto = provider.get_seasons(external_id=data.source_id)

        title, created = update_or_create_title(
            user_id=data.user_id,
            title_dto=title_dto,
            seasons_dto=seasons_dto,
        )

        return {
            "id": title.pk,
            "name": title.name,
            "year": title.year,
            "poster_url": title.poster_url,
            "category": title.category,
            "is_series": title.is_series,
            "created": created,
        }
