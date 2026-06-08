from abc import ABC, abstractmethod

from media.dtos import SearchResultsDTO, SeasonsDTO, TitleDTO


class BaseProvider(ABC):
    slug: str

    @abstractmethod
    def get_title(self, external_id: int, *, force_refresh: bool = False) -> TitleDTO: ...

    @abstractmethod
    def get_seasons(self, external_id: int, *, force_refresh: bool = False) -> SeasonsDTO: ...

    @abstractmethod
    def search(self, query: str, *, page: int = 1) -> SearchResultsDTO: ...
