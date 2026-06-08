from dataclasses import dataclass

from media.dtos import SearchResultsDTO
from media.services.providers.factory import ProviderFactory
from media.usecases.base_usecase import BaseUsecase


@dataclass(frozen=True)
class SearchTitlesInput:
    query: str
    page: int = 1


class SearchTitlesUsecase(BaseUsecase[SearchTitlesInput, SearchResultsDTO]):
    """Usecase поиска тайтлов по названию через провайдера (с кэшем)."""

    def execute(self, data: SearchTitlesInput) -> SearchResultsDTO:
        provider = ProviderFactory.default()
        return provider.search(data.query, page=data.page)
