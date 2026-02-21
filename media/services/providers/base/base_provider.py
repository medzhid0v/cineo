from abc import ABC, abstractmethod

from media.dtos import SeasonsDTO, TitleDTO


class BaseProvider(ABC):
    slug: str

    @abstractmethod
    def get_title(self, external_id: int) -> TitleDTO: ...

    @abstractmethod
    def get_seasons(self, external_id: int) -> SeasonsDTO: ...
