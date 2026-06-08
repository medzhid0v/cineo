import logging

from media.dtos import SearchResultsDTO, SeasonsDTO, TitleDTO
from media.models import PayloadKind
from media.services import payload_cache
from media.services.providers.base import BaseProvider

from .client import KinopoiskClient
from .parser import KinopoiskParser

logger = logging.getLogger(__name__)


# === === === === === === ===
class KinopoiskProvider(BaseProvider):
    slug = "kinopoisk"

    # --- --- --- --- --- --- ---
    def __init__(self, client: KinopoiskClient) -> None:
        self.client = client

    # --- --- --- --- --- --- ---
    def get_title(self, external_id: int, *, force_refresh: bool = False) -> TitleDTO:
        data = self._get_or_fetch(
            external_id=external_id,
            kind=PayloadKind.FILM,
            fetch=lambda: self.client.fetch_film(external_id),
            force_refresh=force_refresh,
        )
        return KinopoiskParser.parse_title(data=data, external_id=external_id)

    # --- --- --- --- --- --- ---
    def get_seasons(self, external_id: int, *, force_refresh: bool = False) -> SeasonsDTO:
        data = self._get_or_fetch(
            external_id=external_id,
            kind=PayloadKind.SEASONS,
            fetch=lambda: self.client.fetch_seasons(external_id),
            force_refresh=force_refresh,
        )
        return KinopoiskParser.parse_seasons(data=data)

    # --- --- --- --- --- --- ---
    def search(self, query: str, *, page: int = 1) -> SearchResultsDTO:
        query = (query or "").strip()
        if not query:
            return SearchResultsDTO()

        # Кэшируем только первую страницу (автокомплит обычно её и показывает).
        if page == 1:
            cached = payload_cache.get_search_payload(self.slug, query)
            if cached is not None:
                return KinopoiskParser.parse_search(cached)

        data = self.client.search_by_keyword(query, page=page)
        if page == 1:
            payload_cache.store_search_payload(self.slug, query, data)
        return KinopoiskParser.parse_search(data)

    # --- --- --- --- --- --- ---
    def _get_or_fetch(self, *, external_id: int, kind: str, fetch, force_refresh: bool) -> dict:
        """
        Возвращает сырой ответ: из кэша, либо из API (с записью в кэш).

        Так повторное добавление тайтла (в т.ч. другим пользователем
        после удаления из UI) не порождает повторный запрос к провайдеру.
        """
        if not force_refresh:
            cached = payload_cache.get_payload(self.slug, external_id, kind)
            if cached is not None:
                logger.debug("Cache hit %s:%s#%s", self.slug, kind, external_id)
                return cached

        data = fetch()
        payload_cache.store_payload(self.slug, external_id, kind, data)
        logger.debug("Cache store %s:%s#%s", self.slug, kind, external_id)
        return data
