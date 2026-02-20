from dataclasses import dataclass

from django.contrib.auth import get_user_model

from media.services.importer import import_title_by_external_id
from media.services.providers.kinopoisk import KinopoiskProvider
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class ReceiveTitle:
    request_user_id: int
    source_id: int


class ReceiveTitleUsecase(BaseUsecase[ReceiveTitle, None]):
    def execute(
        self,
        data: ReceiveTitle,
    ) -> None:
        user = get_user_model().objects.get(pk=data.request_user_id)
        provider = KinopoiskProvider()
        import_title_by_external_id(data.source_id, provider, user)
