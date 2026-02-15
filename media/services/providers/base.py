from typing import Protocol

from media.dtos import SeasonsDTO, TitleDTO


class MediaProvider(Protocol):
    """
    Контракт для провайдеров метаданных (Kinopoisk/TMDB/и т.п.).

    Все провайдеры должны:
    - уметь вернуть базовую карточку произведения по external_id
    - уметь вернуть сезоны/эпизоды (если есть) по external_id
    - возвращать унифицированные DTO из media.services.providers.dtos
    """

    source: str

    def get_title(self, external_id: int) -> TitleDTO: ...

    def get_seasons(self, external_id: int) -> SeasonsDTO: ...
