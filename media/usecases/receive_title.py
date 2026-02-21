from dataclasses import dataclass

from media.services.importer import import_title_by_external_id
from media.services.providers.kinopoisk import KinopoiskProvider
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class ReceiveTitleInput:
    user_id: int
    source_id: int


class ReceiveTitleUsecase(BaseUsecase[ReceiveTitleInput, None]):
    def execute(
        self,
        data: ReceiveTitleInput,
    ) -> None:
        provider = KinopoiskProvider()
        import_title_by_external_id(
            external_id=data.source_id,
            provider=provider,
            user_id=data.user_id,
        )
