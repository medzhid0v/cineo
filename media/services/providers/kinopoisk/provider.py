from media.dtos import SeasonsDTO, TitleDTO
from media.services.providers.base import BaseProvider

from .client import KinopoiskClient
from .parser import KinopoiskParser


# === === === === === === ===
class KinopoiskProvider(BaseProvider):
    source = "kinopoisk"

    # --- --- --- --- --- --- ---
    def __init__(self, client: KinopoiskClient | None = None) -> None:
        self.client = client or KinopoiskClient()

    # --- --- --- --- --- --- ---
    def get_title(self, external_id: int) -> TitleDTO:
        raw = self.client.fetch_film(external_id)
        return KinopoiskParser.parse_title(raw, external_id)

    # --- --- --- --- --- --- ---
    def get_seasons(self, external_id: int) -> SeasonsDTO:
        raw = self.client.fetch_seasons(external_id)
        return KinopoiskParser.parse_seasons(raw)
